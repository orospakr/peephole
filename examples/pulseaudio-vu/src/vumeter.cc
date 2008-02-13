/* $Id: vumeter.cc 43 2006-06-21 14:12:21Z lennart $ */

/***
  This file is part of pavumeter.

  pavumeter is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published
  by the Free Software Foundation; either version 2 of the License,
  or (at your option) any later version.

  pavumeter is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with pavumeter; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
  USA.
***/

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <signal.h>

#include <gtkmm.h>
#include <gtk/gtk.h>

#include <pulse/pulseaudio.h>
#include <pulse/glib-mainloop.h>

#include <dbus/dbus-glib.h>

#define LOGARITHMIC 1

class MainWindow : public Gtk::Window {

public:
    MainWindow(const pa_channel_map &map, const char *source_name);
    virtual ~MainWindow();

protected:

    class ChannelInfo {
    public:
        ChannelInfo(MainWindow &w, const Glib::ustring &l);
      //Gtk::Label *label;
      //Gtk::ProgressBar *progress;
      double fraction;
    };

    std::vector<ChannelInfo*> channels;

    float *levels;

    virtual void addChannel(const Glib::ustring &l);
    virtual bool on_delete_event(GdkEventAny* e);
    virtual bool on_display_timeout();
    virtual bool on_calc_timeout();
    virtual void decayLevels();

    DBusGProxy *dbusproxy;
    void startDBus();
    void sendVUToLCD(double lev);

    sigc::connection display_timeout_signal_connection;
    sigc::connection calc_timeout_signal_connection;
    pa_usec_t latency;

    class LevelInfo {
    public:
        LevelInfo(float *levels, pa_usec_t l);
        virtual ~LevelInfo();
        bool elapsed();

        struct timeval tv;
        float *levels;
    };

    std::deque<LevelInfo *> levelQueue;

public:
    virtual void pushData(const float *d, unsigned l);
    virtual void showLevels(const LevelInfo& i);
    virtual void updateLatency(pa_usec_t l);
};

MainWindow::MainWindow(const pa_channel_map &map, const char *source_name) :
    Gtk::Window(),
    //    table(1, 2),
    latency(0) {

    char t[256];
    int n;

    printf("Showing signal levels of source <b>%s</b>.", source_name);

    for (n = 0; n < map.channels; n++) {
        snprintf(t, sizeof(t), "<b>%s:</b>", pa_channel_position_to_string(map.map[n]));
        addChannel(t);
    }

    g_assert(channels.size() == map.channels);

    levels = NULL;
    display_timeout_signal_connection = Glib::signal_timeout().connect(sigc::mem_fun(*this, &MainWindow::on_display_timeout), 10);
    calc_timeout_signal_connection = Glib::signal_timeout().connect(sigc::mem_fun(*this, &MainWindow::on_calc_timeout), 50);

    startDBus();
}

MainWindow::~MainWindow() {
    while (channels.size() > 0) {
        ChannelInfo *i = channels.back();
        channels.pop_back();
        delete i;
    }

    while (levelQueue.size() > 0) {
        LevelInfo *i = levelQueue.back();
        levelQueue.pop_back();
        delete i;
    }

    if (levels)
        delete[] levels;

    display_timeout_signal_connection.disconnect();
    calc_timeout_signal_connection.disconnect();
}

bool MainWindow::on_delete_event(GdkEventAny*) {
    Gtk::Main::quit();
    return true;
}

void MainWindow::addChannel(const Glib::ustring &l) {
    channels.push_back(new ChannelInfo(*this, l));
}

MainWindow::ChannelInfo::ChannelInfo(MainWindow &w, const Glib::ustring &l) {
}

void MainWindow::pushData(const float *d, unsigned samples) {
    unsigned nchan = channels.size();

    if (!levels) {
        levels = new float[nchan];
        for (unsigned c = 0; c < nchan; c++)
            levels[c] = 0;
    }

    while (samples >= nchan) {

        for (unsigned c = 0; c < nchan; c++) {
            float v = fabs(d[c]);
            if (v > levels[c])
                levels[c] = v;
        }

        d += nchan;
        samples -= nchan;
    }
}

void MainWindow::showLevels(const LevelInfo &i) {
    unsigned nchan = channels.size();

    g_assert(i.levels);

    for (unsigned n = 0; n < nchan; n++) {
        double level;
        ChannelInfo *c = channels[n];

        level = i.levels[n];

#ifdef LOGARITHMIC
        level = log10(level*9+1);
#endif

        //if (n == 0) {
            printf("%f\n" ,level);
            //}
            c->fraction = (level > 1 ? 1 : level);
            sendVUToLCD(c->fraction);
        //c->progress->set_fraction(level > 1 ? 1 : level);
    }

}

#define DECAY_LEVEL (0.005)

void MainWindow::decayLevels() {
    unsigned nchan = channels.size();

    for (unsigned n = 0; n < nchan; n++) {
        double level;

        ChannelInfo *c = channels[n];

        level = c->fraction; // andrew come back here

        if (level <= 0)
            continue;

        level = level > DECAY_LEVEL ? level - DECAY_LEVEL : 0;
        c->fraction = level;
        //sendVUToLCD(c->fraction);
    }
}

void MainWindow::startDBus() {
    DBusGConnection *connection;
    GError *error;
    //DBusGProxy *proxy;

    error = NULL;
    connection = dbus_g_bus_get(DBUS_BUS_SYSTEM,
                                &error);
    if (connection == NULL) {
        g_printerr("Failed to open connection to bus: %s\n",
                   error->message);
        g_error_free(error);
        exit(1);
    }

    dbusproxy = dbus_g_proxy_new_for_name(connection,
                                           "ca.infoglobe.peephole",
                                           "/ca/infoglobe/peephole/LCDs/GTK",
                                           "ca.infoglobe.peephole.LCD");

}

void MainWindow::sendVUToLCD(double lev) {
    if (lev > 1.0) {
        lev = 1.0;
    }
    dbus_g_proxy_call_no_reply(dbusproxy, "DrawVUMeter", G_TYPE_DOUBLE,
                               lev, G_TYPE_INVALID, G_TYPE_INVALID);
}


bool MainWindow::on_display_timeout() {
    LevelInfo *i = NULL;

    if (levelQueue.empty()) {
        decayLevels();
        return true;
    }

    while (levelQueue.size() > 0) {
        if (i)
            delete i;

        i = levelQueue.back();
        levelQueue.pop_back();

        if (!i->elapsed())
            break;
    }

    if (i) {
        showLevels(*i);
        delete i;
    }

    return true;
}

bool MainWindow::on_calc_timeout() {
    if (levels) {
        levelQueue.push_front(new LevelInfo(levels, latency));
        levels = NULL;
    }

    return true;
}

void MainWindow::updateLatency(pa_usec_t l) {
    latency = l;
}

static void timeval_add_usec(struct timeval *tv, pa_usec_t v) {
    uint32_t sec = v/1000000;
    tv->tv_sec += sec;
    v -= sec*1000000;

    tv->tv_usec += v;

    while (tv->tv_usec >= 1000000) {
        tv->tv_sec++;
        tv->tv_usec -= 1000000;
    }
}

MainWindow::LevelInfo::LevelInfo(float *l, pa_usec_t latency) {
    levels = l;
    gettimeofday(&tv, NULL);
    timeval_add_usec(&tv, latency);
}

MainWindow::LevelInfo::~LevelInfo() {
    delete[] levels;
}

bool MainWindow::LevelInfo::elapsed() {
    struct timeval now;
    gettimeofday(&now, NULL);

    if (now.tv_sec != tv.tv_sec)
        return now.tv_sec > tv.tv_sec;

    return now.tv_usec >= tv.tv_usec;
}

static MainWindow *mainWindow = NULL;
static pa_context *context = NULL;
static pa_stream *stream = NULL;
static char* device_name = NULL;
static enum {
    PLAYBACK,
    RECORD
} mode = PLAYBACK;


void show_error(const char *txt, bool show_pa_error = true) {
    char buf[256];

    if (show_pa_error)
        snprintf(buf, sizeof(buf), "%s: %s", txt, pa_strerror(pa_context_errno(context)));

    //    Gtk::MessageDialog dialog(show_pa_error ? buf : txt, false, Gtk::MESSAGE_ERROR, Gtk::BUTTONS_CLOSE, true);
    fprintf(stderr, buf);

    Gtk::Main::quit();
}

static void stream_update_timing_info_callback(pa_stream *s, int success, void *) {
    pa_usec_t t;
    int negative = 0;

    if (!success || pa_stream_get_latency(s, &t, &negative) < 0) {
        show_error("Failed to get latency information");
        return;
    }

    if (!mainWindow)
        return;

    mainWindow->updateLatency(negative ? 0 : t);
}

static gboolean latency_func(gpointer) {
    pa_operation *o;

    if (!stream)
        return false;

    if (!(o = pa_stream_update_timing_info(stream, stream_update_timing_info_callback, NULL)))
        g_message("pa_stream_update_timing_info() failed: %s", pa_strerror(pa_context_errno(context)));
    else
        pa_operation_unref(o);

    return true;
}

static void stream_read_callback(pa_stream *s, size_t l, void *) {
    const void *p;
    g_assert(mainWindow);

    if (pa_stream_peek(s, &p, &l) < 0) {
        g_message("pa_stream_peek() failed: %s", pa_strerror(pa_context_errno(context)));
        return;
    }

    mainWindow->pushData((const float*) p, l/sizeof(float));

    pa_stream_drop(s);
}

static void stream_state_callback(pa_stream *s, void *) {
    switch (pa_stream_get_state(s)) {
        case PA_STREAM_UNCONNECTED:
        case PA_STREAM_CREATING:
            break;

        case PA_STREAM_READY:
            g_assert(!mainWindow);
            mainWindow = new MainWindow(*pa_stream_get_channel_map(s), device_name);

            g_timeout_add(100, latency_func, NULL);
            pa_operation_unref(pa_stream_update_timing_info(stream, stream_update_timing_info_callback, NULL));
            break;

        case PA_STREAM_FAILED:
            show_error("Connection failed");
            break;

        case PA_STREAM_TERMINATED:
            Gtk::Main::quit();
    }
}

static void create_stream(const char *name, const pa_sample_spec &ss, const pa_channel_map &cmap) {
    char t[256];
    pa_sample_spec nss;

    g_free(device_name);
    device_name = g_strdup(name);

    nss.format = PA_SAMPLE_FLOAT32;
    nss.rate = ss.rate;
    nss.channels = ss.channels;

    g_message("Using sample format: %s", pa_sample_spec_snprint(t, sizeof(t), &nss));
    g_message("Using channel map: %s", pa_channel_map_snprint(t, sizeof(t), &cmap));

    stream = pa_stream_new(context, "PulseAudio Volume Meter", &nss, &cmap);
    pa_stream_set_state_callback(stream, stream_state_callback, NULL);
    pa_stream_set_read_callback(stream, stream_read_callback, NULL);
    pa_stream_connect_record(stream, name, NULL, (enum pa_stream_flags) 0);
}

static void context_get_source_info_callback(pa_context *, const pa_source_info *si, int is_last, void *) {
    if (is_last < 0) {
        show_error("Failed to get source information");
        return;
    }

    if (!si)
        return;

    create_stream(si->name, si->sample_spec, si->channel_map);
}

static void context_get_sink_info_callback(pa_context *, const pa_sink_info *si, int is_last, void *) {
    if (is_last < 0) {
        show_error("Failed to get sink information");
        return;
    }

    if (!si)
        return;

    create_stream(si->monitor_source_name, si->sample_spec, si->channel_map);
}

static void context_get_server_info_callback(pa_context *c, const pa_server_info*si, void *) {
    if (!si) {
        show_error("Failed to get server information");
        return;
    }

    if (mode == PLAYBACK) {

        if (!si->default_sink_name) {
            show_error("No default sink set.", false);
            return;
        }

        pa_operation_unref(pa_context_get_sink_info_by_name(c, si->default_sink_name, context_get_sink_info_callback, NULL));

    } else if (mode == RECORD) {

        if (!si->default_source_name) {
            show_error("No default source set.", false);
            return;
        }

        pa_operation_unref(pa_context_get_source_info_by_name(c, si->default_source_name, context_get_source_info_callback, NULL));
    }
}

static void context_state_callback(pa_context *c, void *) {
    switch (pa_context_get_state(c)) {
        case PA_CONTEXT_UNCONNECTED:
        case PA_CONTEXT_CONNECTING:
        case PA_CONTEXT_AUTHORIZING:
        case PA_CONTEXT_SETTING_NAME:
            break;

        case PA_CONTEXT_READY:
            g_assert(!stream);

            if (device_name && mode == RECORD)
                pa_operation_unref(pa_context_get_source_info_by_name(c, device_name, context_get_source_info_callback, NULL));
            else if (device_name && mode == PLAYBACK)
                pa_operation_unref(pa_context_get_sink_info_by_name(c, device_name, context_get_sink_info_callback, NULL));
            else
                pa_operation_unref(pa_context_get_server_info(c, context_get_server_info_callback, NULL));

            break;

        case PA_CONTEXT_FAILED:
            show_error("Connection failed");
            break;

        case PA_CONTEXT_TERMINATED:
            Gtk::Main::quit();
    }
}

int main(int argc, char *argv[]) {
    pa_glib_mainloop *m;
    bool record;

    signal(SIGPIPE, SIG_IGN);

    Glib::OptionGroup og("PulseAudio Volume Meter", "Control the volume of your PulseAudio Sound Server");

    Glib::OptionEntry oe;
    oe.set_long_name("record");
    oe.set_description("Show Record Levels");
    og.add_entry(oe, record);

    Glib::OptionContext oc;
    oc.set_main_group(og);

    Gtk::Main kit(argc, argv, oc);

    mode = record ? RECORD : PLAYBACK;

    g_message("Starting in %s mode.", mode == RECORD ? "record" : "playback");

    /* Rather ugly and incomplete */
    if (argc > 1)
        device_name = g_strdup(argv[1]) ;
    else {
        char *e;
        if ((e = getenv(mode == RECORD ? "PULSE_SOURCE" : "PULSE_SINK")))
            device_name = g_strdup(e);
    }

    if (device_name)
        g_message("Using device '%s'", device_name);

    m = pa_glib_mainloop_new(g_main_context_default());
    g_assert(m);

    context = pa_context_new(pa_glib_mainloop_get_api(m), "PulseAudio Volume Meter");
    g_assert(context);

    pa_context_set_state_callback(context, context_state_callback, NULL);
    pa_context_connect(context, NULL, PA_CONTEXT_NOAUTOSPAWN, NULL);

    Gtk::Main::run();

    if (stream)
        pa_stream_unref(stream);
    if (context)
        pa_context_unref(context);

    if (mainWindow)
        delete mainWindow;

    if(device_name)
        g_free(device_name);

    pa_glib_mainloop_free(m);

    return 0;
}
