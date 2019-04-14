/*
 * ob3_theme.c-v0.07.2:
 *   ob3_theme is an openbox3 pipe-menu program that generates an xml menu
 *   based on available themes. The menu entry can be clicked to change to
 *   the selected theme.
 *
 * Requirements:
 *   openbox 3.0    - http://www.openbox.org/
 *   gtk+ 2.x       - http://www.gtk.org/
 *
 * Compiling:
 *   gcc -Wall -O2 `pkg-config --cflags gtk+-2.0 obparser-3.0` ob3_theme.c -o \
 *       ob3_theme `pkg-config --libs gtk+-2.0 obparser-3.0`
 *
 * Usage:
 *   ~/.config/openbox/rc.xml:
 *     <theme>
 *       <name>~/.config/ob3_theme/theme</name>
 *     </theme>
 *
 *   ~/.config/openbox/menu.xml:
 *     <menu id="ob3_theme" label="Themes" execute="ob3_theme" />
 *
 * Created Files/Directories:
 *   ~/.config/ob3_theme
 *   ~/.config/ob3_theme/theme   (current theme, symlink)
 *
 * Notes:
 *   ob3_theme does NOT modify your config. Instead, when rc.xml is configured
 *   as above, openbox uses a symlink. This symlink is managed by ob3_theme.
 *
 *   The theme currently in use will be denoted with an arrow.
 *
 * (c) 2003 Mike Hokenson <logan at dct dot com>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. The name of the author may not be used to endorse or promote products
 *    derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include <unistd.h>

#include <gdk/gdk.h>

#include <openbox/parse.h>

#if (!defined(OB_CHECK_VERSION) || !OB_CHECK_VERSION(3, 0, 2))
# error "Openbox 3.0 is required."
#endif

#define VERSION        "0.07.2"
#define PROGRAM        "ob3_theme"
#define URL            "http://www.gozer.org/programs/c/"

/* -- openbox pipe-menu helper functions ------------------------------------ */

gboolean ob3_pipemenu_start = FALSE;

xmlDocPtr ob3_pipemenu_doc;
xmlNodePtr ob3_pipemenu_node;

/*
 * ob3_pipemenu_startup:
 *   initialize pipe-menu helper functions, setup xmlDocPtr, xmlNodePtr.
 */
void ob3_pipemenu_startup(void)
{
    g_return_if_fail(ob3_pipemenu_start != TRUE);

    ob3_pipemenu_start = TRUE;
    ob3_pipemenu_doc = xmlNewDoc((xmlChar *) "1.0");
    ob3_pipemenu_node = xmlNewDocNode(ob3_pipemenu_doc, NULL,
                                      (xmlChar *) "openbox_pipe_menu", NULL);
    xmlDocSetRootElement(ob3_pipemenu_doc, ob3_pipemenu_node);
}

/*
 * ob3_pipemenu_shutdown:
 *   free used xml memory, set ob3_pipemenu_start to FALSE.
 */
void ob3_pipemenu_shutdown(void)
{
    xmlFreeDoc(ob3_pipemenu_doc);

    ob3_pipemenu_start = FALSE;
}

/*
 * ob3_pipemenu_display:
 *   @name: string to use for character encoding, UTF-8 is used if NULL.
 *
 *   print xml data if child nodes exist.
 */
void ob3_pipemenu_display(const gchar *encoding)
{
    g_return_if_fail(ob3_pipemenu_start != FALSE);

    if(ob3_pipemenu_node->children)
        xmlSaveFormatFileEnc("-", ob3_pipemenu_doc, encoding, 1);
}

/*
 * ob3_pipemenu_node_add:
 *   @node:  xmlNodePtr to use, if NULL toplevel is used.
 *   @name:  string to use for node name.
 *   @value: string to use for node value, NULL can be used for no node value.
 *
 *   adds a property to the specified node.
 *
 *   <@name>@value</@name>
 */
xmlNodePtr ob3_pipemenu_node_add(xmlNodePtr node, const gchar *name,
                                                  const gchar *value)
{
    xmlNodePtr n = (node) ? node : ob3_pipemenu_node;

    g_return_val_if_fail(ob3_pipemenu_start != FALSE, NULL);
    g_return_val_if_fail(name != NULL, NULL);

    return(xmlNewTextChild(n, NULL, (xmlChar *) name, (xmlChar *) value));
}

/*
 * ob3_pipemenu_node_set_prop:
 *   @node:  xmlNodePtr to use, if NULL toplevel is used.
 *   @name:  string to use for property name.
 *   @value: string to use for property.
 *
 *   adds a property to the specified node.
 *
 *   <@node @name="@value" />
 */
void ob3_pipemenu_node_set_prop(xmlNodePtr node, const gchar *name,
                                                 const gchar *value)
{
    xmlNodePtr n = (node) ? node : ob3_pipemenu_node;

    g_return_if_fail(ob3_pipemenu_start != FALSE);
    g_return_if_fail(name != NULL);

    xmlSetProp(n, (xmlChar *) name, (xmlChar *) value);
}

/*
 * ob3_pipemenu_separator_add:
 *   @node:  xmlNodePtr to use, if NULL toplevel is used.
 *
 *   adds a separator to the openbox pipe-menu.
 *
 *   <separator />
 */
void ob3_pipemenu_separator_add(xmlNodePtr node)
{
    xmlNodePtr n = (node) ? node : ob3_pipemenu_node;

    g_return_if_fail(ob3_pipemenu_start != FALSE);

    ob3_pipemenu_node_add(n, "separator", NULL);
}

/*
 * ob3_pipemenu_menu_add:
 *   @node:  xmlNodePtr to use, if NULL toplevel is used.
 *   @label: string to use for menu label.
 *   @id:    string to use for menu-id.
 *
 *   adds a menu to the openbox pipe-menu, returns xmlNodePtr.
 *
 *   <menu id="@id" label="@label">
 *   </menu>
 */
xmlNodePtr ob3_pipemenu_menu_add(xmlNodePtr node, const gchar *label,
                                                  const gchar *id)
{
    xmlNodePtr n = (node) ? node : ob3_pipemenu_node;
    xmlNodePtr p;

    g_return_val_if_fail(ob3_pipemenu_start != FALSE, NULL);
    g_return_val_if_fail(id    != NULL, NULL);
    g_return_val_if_fail(label != NULL, NULL);

    if((p = ob3_pipemenu_node_add(n, "menu", NULL))) {
        ob3_pipemenu_node_set_prop(p, "id", id);
        ob3_pipemenu_node_set_prop(p, "label", label);
    }

    return(p);
}

/*
 * ob3_pipemenu_action_add:
 *   @node:    xmlNodePtr to use, if NULL toplevel is used.
 *   @action:  string to use for action name.
 *   @execute: string to use for execute action. if NULL execute is excluded.
 *
 *   adds an action to a node item, returns xmlNodePtr.
 *
 *   <action name="@action">
 *     <execute>@execute</execute>
 *   </action>
 */
xmlNodePtr ob3_pipemenu_action_add(xmlNodePtr node, const gchar *action,
                                                    const gchar *execute)
{
    xmlNodePtr n = (node) ? node : ob3_pipemenu_node;
    xmlNodePtr p;

    g_return_val_if_fail(ob3_pipemenu_start != FALSE, NULL);
    g_return_val_if_fail(action != NULL, NULL);

    if((p = ob3_pipemenu_node_add(n, "action", NULL))) {
        ob3_pipemenu_node_set_prop(p, "name", action);

        if(execute && execute[0])
            ob3_pipemenu_node_add(p, "execute", execute);
    }

    return(p);
}

/*
 * ob3_pipemenu_item_add:
 *   @node:   xmlNodePtr to use, if NULL toplevel is used.
 *   @label:  string to use for item label.
 *   @action: string to use for execute action. if NULL action is excluded.
 *
 *   adds a menu item to the openbox pipe-menu, returns xmlNodePtr.
 *
 *   <item label="@label">
 *     <action name="Execute">
 *       <execute>@action</execute>
 *     </action>
 *   </item>
 */
xmlNodePtr ob3_pipemenu_item_add(xmlNodePtr node, const gchar *label,
                                                  const gchar *action)
{
    xmlNodePtr n = (node) ? node : ob3_pipemenu_node;
    xmlNodePtr p;

    g_return_val_if_fail(ob3_pipemenu_start != FALSE, NULL);
    g_return_val_if_fail(label != NULL, NULL);

    if((p = ob3_pipemenu_node_add(n, "item", NULL))) {
        ob3_pipemenu_node_set_prop(p, "label", label);

        if(action && action[0])
            ob3_pipemenu_action_add(p, "Execute", action);
    }

    return(p);
}

/* -- openbox pipe-menu helper functions ------------------------------------ */

#ifndef PATH_MAX
# ifdef MAXPATHLEN
#  define PATH_MAX     MAXPATHLEN
# else
#  define PATH_MAX     1024
# endif
#endif

#define G_ERROR        ((g_strerror(errno)))

#define IS_FILE(s)     ((g_file_test(s, G_FILE_TEST_IS_REGULAR)))
#define IS_DIR(s)      ((g_file_test(s, G_FILE_TEST_IS_DIR)))
#define IS_LINK(s)     ((g_file_test(s, G_FILE_TEST_IS_SYMLINK)))

#define OB3_CLI_ARG(argv1, s, l) (!strcmp(argv1, s) || strstr(argv1, l))

#define _OB3_DEFAULT   "TheBear"

struct ob3_theme_t {
    gchar *path;   /* path to theme dir (/usr/local/share/themes/TheBear) */
    gchar *name;   /* theme name (TheBear) */
};

void ob3_init(gint argc, gchar **argv);
void ob3_exit(gint level);

void ob3_theme_menu_create(void);
void ob3_theme_use(const gchar *theme);

void ob3_usage(void);
void ob3_version(void);

gchar *ob3_theme_home, *ob3_theme_path, *ob3_theme_file;

GSList *ob3_theme_list;

gint main(gint argc, gchar **argv)
{
    ob3_init(argc, argv); /* setup variables, theme slist */

    if(argc > 2) {
        ob3_usage();
        ob3_exit(1);
    }

    if(argc == 2) {
        if(OB3_CLI_ARG(argv[1], "-h", "-help")) {
            ob3_usage();
            ob3_exit(0);
        }

        if(OB3_CLI_ARG(argv[1], "-v", "-version")) {
            ob3_version();
            ob3_exit(0);
        }
    }

    if(argc > 1) {
        gdk_init(&argc, &argv);
        ob3_theme_use(argv[1]);
    } else
        ob3_theme_menu_create();

    ob3_exit(0);

    exit(0); /* not reached */
}

gchar *ob3_readlink(const gchar *path)
{
    gchar *buf;

    gint len;

    g_return_val_if_fail(path != NULL, NULL);

    if(!IS_LINK(path))
        return(NULL);

    buf = g_malloc(PATH_MAX + 1);

    if((len = readlink(path, buf, PATH_MAX)) == -1) {
        g_critical("unable to readlink %s: %s", path, G_ERROR);
        ob3_exit(1);
    }

    buf[len] = '\0';

    return(buf);
}

void ob3_symlink(const gchar *theme, const gchar *path)
{
    g_return_if_fail(theme != NULL);
    g_return_if_fail(path  != NULL);

    if(symlink(theme, path) == -1) {
        g_critical("unable to symlink %s to %s: %s", theme, path, G_ERROR);
        ob3_exit(1);
    }
}

gboolean ob3_is_theme_dir(const gchar *path)
{
    gboolean is_theme_dir;

    g_return_val_if_fail(path != NULL, FALSE);

    if(!IS_DIR(path))
        return(FALSE);

    {
        gchar *rc = g_build_filename(path, "openbox-3", "themerc", NULL);
        is_theme_dir = IS_FILE(rc);
        g_free(rc);
    }

    return(is_theme_dir);
}

/* scan each directory looking for the ThemeName directory */
gchar *ob3_theme_locate(const gchar *name)
{
    GSList *p;

    g_return_val_if_fail(name != NULL, NULL);

    /* see if the name specified on the command line is already a full path */
    if(ob3_is_theme_dir(name))
        return(g_strdup(name));

    /* just ThemeName, scan all diectories */
    for(p = parse_xdg_data_dir_paths(); p; p = g_slist_next(p)) {
        gchar *path = g_build_filename(p->data, "themes", name, NULL);

        if(ob3_is_theme_dir(path))
            return(path);
        else
            g_free(path);
    }

    return(NULL);
}

/* get the theme name from ~/.config/openbox/rc.xml */
gchar *ob3_theme_from_openbox_config(void)
{
    gchar *config_theme = NULL;

    xmlDocPtr doc;
    xmlNodePtr node;

#if (OB_CHECK_VERSION(3, 4, 0))
    if(parse_load_rc(NULL, &doc, &node)) {
#else
    if(parse_load_rc(&doc, &node)) {
#endif
        xmlNodePtr n;

        if((n = parse_find_node("theme", node->children))) {
            if((n = parse_find_node("name", n->children))) {
                gchar *p = parse_string(doc, n);
                if(p && p[0])
                    config_theme = parse_expand_tilde(p);
                g_free(p);
            }
        }
    }

    parse_close(doc);

    if(config_theme) {
        gchar *p = ob3_theme_locate(config_theme);
        g_free(config_theme);
        return(p);
    }

    return(NULL);
}

void ob3_init(gint argc, gchar **argv)
{
    g_set_prgname(argv[0]);

    ob3_pipemenu_startup();

    parse_paths_startup();

    ob3_theme_home = g_build_filename(parse_xdg_config_home_path(),
                                      "ob3_theme", NULL);

    /* ~/.config/ob3_theme/theme (symlink used for setting up new themes) */
    ob3_theme_path = g_build_filename(ob3_theme_home, "theme", NULL);

    /* slist containing all available openbox themes */
    ob3_theme_list = NULL;

    /* try ob3_theme symlink, ob3 config file, finally default to 'TheBear' */
    if(!(ob3_theme_file = ob3_readlink(ob3_theme_path)))
        if(!(ob3_theme_file = ob3_theme_from_openbox_config()))
            ob3_theme_file = ob3_theme_locate(_OB3_DEFAULT);

    if(!parse_mkdir_path(parse_xdg_config_home_path(), 0755))
        ob3_exit(1);

    if(!parse_mkdir(ob3_theme_home, 0755))
        ob3_exit(1);

    /* setup the default symlink for immediate usage in rc.xml */
    if(!IS_LINK(ob3_theme_path))
        ob3_symlink(ob3_theme_file, ob3_theme_path);
}

void ob3_theme_free(struct ob3_theme_t *theme)
{
    g_return_if_fail(theme != NULL);

    g_free(theme->path);
    g_free(theme->name);

    g_free(theme);
}

void ob3_exit(gint level)
{
    g_free(ob3_theme_home);
    g_free(ob3_theme_path);
    g_free(ob3_theme_file);

    g_slist_foreach(ob3_theme_list, (GFunc) ob3_theme_free, NULL);
    g_slist_free(ob3_theme_list);

    parse_paths_shutdown();

    ob3_pipemenu_display("UTF-8");

    ob3_pipemenu_shutdown();

    exit(level);
}

void ob3_openbox_reconfigure(void)
{
    guchar *data;

    pid_t pid;

    if(!gdk_property_get(gdk_screen_get_root_window(gdk_screen_get_default()),
                         gdk_atom_intern("_OPENBOX_PID", FALSE),
                         gdk_atom_intern("CARDINAL", FALSE),
                         0,
                         sizeof(guchar *),
                         FALSE,
                         NULL,
                         0,
                         0,
                         &data)) {
        g_critical("unable to get _OPENBOX_PID, not running openbox3?");
        ob3_exit(1);
    }

    pid = (pid_t) * (pid_t *) data;

    g_free(data);

    /* make sure the pid is valid and running (by the current user) */
    if(pid < 1 || kill(pid, 0) == -1) {
        g_critical("invalid openbox pid? (%lu): %s", (gulong) pid, G_ERROR);
        ob3_exit(1);
    }

    if(kill(pid, SIGUSR2) == -1) {
        g_critical("unable reconfigure openbox: %s", G_ERROR);
        ob3_exit(1);
    }
}

gint ob3_theme_name_cmp(struct ob3_theme_t *a, struct ob3_theme_t *b)
{
    return(strcmp(a->name, b->name));
}

/* adds the available openbox themes to ob3_theme_list slist */
void ob3_process_theme_dir(const gchar *dir)
{
    const gchar *p;

    GDir *dp;

    g_return_if_fail(dir != NULL);

    if(!IS_DIR(dir))
        return;

    if(!(dp = g_dir_open(dir, 0, NULL))) {
        g_warning("unable to open %s: %s", dir, G_ERROR);
        return;
    }

    while((p = g_dir_read_name(dp))) {
        gchar *path = g_build_filename(dir, p, NULL);

        if(ob3_is_theme_dir(path)) {
            struct ob3_theme_t *theme;

            theme       = g_new(struct ob3_theme_t, 1);
            theme->path = path;
            theme->name = g_path_get_basename(path);

            ob3_theme_list = g_slist_insert_sorted(ob3_theme_list, theme,
                                 (GCompareFunc) ob3_theme_name_cmp);
        } else
            g_free(path);
    }

    g_dir_close(dp);
}

/* displays openbox pipe-menu xml output */
void ob3_theme_menu_create(void)
{
    GSList *p;

    for(p = parse_xdg_data_dir_paths(); p; p = g_slist_next(p)) {
        gchar *path = g_build_filename(p->data, "themes", NULL);
        ob3_process_theme_dir(path);
        g_free(path);
    }

    if(!ob3_theme_list) {
        ob3_pipemenu_item_add(NULL, "No Themes Found", NULL);
        return;
    }

    for(p = ob3_theme_list; p; p = g_slist_next(p)) {
        struct ob3_theme_t *theme = p->data;
        gchar *label, *action, *s;

        if(!theme || !theme->path || !theme->name)
            continue;

        if(ob3_theme_file && !strcmp(theme->path, ob3_theme_file))
            label = g_strconcat(theme->name, " <-", NULL);
        else
            label = g_strdup(theme->name);

        s = g_shell_quote(theme->path);
        action = g_strconcat(g_get_prgname(), " ", s, NULL);
        g_free(s);

        ob3_pipemenu_item_add(NULL, label, action);

        g_free(label);
        g_free(action);
    }
}

/* remove the ~/.config/ob3_theme/theme symlink */
void ob3_unlink(const gchar *path)
{
    g_return_if_fail(path != NULL);

    if(!IS_LINK(path))
        return;

    if(unlink(path) == -1) {
        g_critical("unable to remove %s: %s", path, G_ERROR);
        ob3_exit(1);
    }
}

/* sets up the ~/.config/ob3_theme/theme symlink, reconfigures openbox */
void ob3_theme_use(const gchar *name)
{
    gchar *path;

    g_return_if_fail(name != NULL);

    if(!(path = ob3_theme_locate(name))) {
        g_critical("unable to locate theme \"%s\"", name);
        ob3_exit(1);
    }

    /* remove ~/.config/ob3_theme/theme symlink */
    ob3_unlink(ob3_theme_path);

    /* symlink /path/ThemeName to ~/.config/ob3_theme/theme */
    ob3_symlink(path, ob3_theme_path);

    /* Reconfigure openbox, send SIGUSR2 */
    ob3_openbox_reconfigure();
}

void ob3_usage(void)
{
    const gchar *prog = g_get_prgname();

    ob3_version();

    fprintf(stderr, "\n");
    fprintf(stderr, "Usage: %s <theme>\n\n", prog);

    fprintf(stderr, "  Examples:\n");
    fprintf(stderr, "    %s\n", prog);
    fprintf(stderr, "    %s %s\n\n", prog, _OB3_DEFAULT);

    fprintf(stderr, "  Usage:\n");
    fprintf(stderr, "    ~/.config/openbox/rc.xml:\n");
    fprintf(stderr, "      <theme>\n");
    fprintf(stderr, "        <name>~/.config/ob3_theme/theme</name>\n");
    fprintf(stderr, "      </theme>\n\n");

    fprintf(stderr, "    ~/.config/openbox/menu.xml:\n");
    fprintf(stderr, "      <menu id=\"ob3_theme\" label=\"Themes\" ");
    fprintf(stderr, "execute=\"%s\" />\n", prog);
}

void ob3_version(void)
{
    fprintf(stderr, "%s v%s (%s)\n", PROGRAM, VERSION, URL);
}

/*
 * --- Changelog --------------------------------------------------------------
 *
 *  0.01 - 2003/09/23:
 *    initial release.
 *
 *  0.02 - 2003/10/17:
 *    x[ht]ml-ize the name to allow for themes containing <>&'" or other
 *      characters the xml parser may not like.
 *    use g_warning() instead of g_warning().
 *
 *  0.03 - 2003/10/21:
 *    relocated configuration to ~/.config/ob3_theme.
 *    include openbox/parse.h for XDG related functions.
 *    remove glib.h include (already included with openbox/parser.h).
 *
 *  0.04 - 2003/10/22:
 *    use full path to theme directory instead of the name. this allows for
 *      multiple themes with the same name, but only one is denoted.
 *    add recursive mkdir for ~/.config (or $XDG_CONFIG_HOME).
 *    fix improper g_return_[val]if_fail() usage.
 *    other cleanups.
 *
 *  0.05 - 2003/11/07:
 *    require openbox 3.0. remove ob3_mkdir* and use parse_mkdir*, dupe check.
 *    make ob3_readlink() return an allocated buffer.
 *    move parse_paths_shutdown() to ob3_exit().
 *    updated ob3_string_to_xml_safe() to only encode <>&'" and non-printable
 *      characters.
 *    use g_shell_quote() on paths.
 *    use g_warning() instead of ob3_error().
 *    use g_path_get_basename() instead of deprecated g_basename().
 *    when creating ~/.config/ob3_theme/theme symlink, first try the openbox
 *      config file, then fallback to 'TheBear'.
 *    reworked gdk_property_get() call to get _OPENBOX_PID.
 *    other cleanups.
 *
 *  0.06 - 2003/11/15:
 *    add in pipe-menu helpers, use xml functions to print the created menu.
 *      removed ob3_string_to_xml_safe().
 *    use g_critical() in appropriate situations.
 *
 *  0.07 - 2004/11/08:
 *    minor cleanups.
 *
 *  0.07.1 - 2006/08/27:
 *    fix libxml signedness warnings
 *
 * --- Changelog --------------------------------------------------------------
 */
