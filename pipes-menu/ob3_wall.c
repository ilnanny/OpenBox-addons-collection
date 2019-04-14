/*
 * ob3_wall.c-v0.08.1:
 *   ob3_wall is an openbox3 pipe-menu program that generates an xml menu
 *   based on available wallpaper. The menu entry can be clicked to change to
 *   the current wallpaper.
 *
 * Requirements:
 *   openbox 3.0    - http://www.openbox.org/
 *
 * Compiling:
 *   gcc -Wall -O2 `pkg-config --cflags obparser-3.0` ob3_wall.c -o \
 *      ob3_wall `pkg-config --libs obparser-3.0`
 *
 * Usage:
 *   ~/.config/openbox/menu.xml:
 *     <menu id="ob3_wall" label="Wallpaper" execute="ob3_wall" />
 *
 * Created Files/Directories:
 *   ~/.config/ob3_wall
 *   ~/.config/ob3_wall/rc.xml   (configuration)
 *   ~/.config/ob3_wall/wall     (current wallpaper, symlink)
 *
 * Notes:
 *   ob3_wall creates a menu with all files found in the specified directories.
 *   There is no special check for known image types, it is assumed any files
 *   in these directories would be images only.
 *
 *   ob3_wall can be used in ~/.xinitrc to setup the wallpaper selected from
 *   a previous X session, just add in 'ob3_wall -' before openbox.
 *
 *   The wallpaper currently in use will be denoted with an arrow.
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
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include <openbox/parse.h>

#if (!defined(OB_CHECK_VERSION) || !OB_CHECK_VERSION(3, 0, 2))
# error "Openbox 3.0 is required."
#endif

#define VERSION        "0.08.1"
#define PROGRAM        "ob3_wall"
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

#ifndef LINE_MAX
#define LINE_MAX       2048
#endif

#define G_ERROR        ((g_strerror(errno)))

#define IS_FILE(s)     ((g_file_test(s, G_FILE_TEST_IS_REGULAR)))
#define IS_DIR(s)      ((g_file_test(s, G_FILE_TEST_IS_DIR)))
#define IS_LINK(s)     ((g_file_test(s, G_FILE_TEST_IS_SYMLINK)))

#define OB3_CLI_ARG(argv1, s, l) (!strcmp(argv1, s) || strstr(argv1, l))

struct ob3_wall_t {
    gchar *path;   /* full path to wallpaper file */
    gchar *name;   /* wallpaper file */
};

struct ob3_wall_loader_t {
    const gchar *name;
    const gchar *cmd;
};

/* list taken from bsetbg */
struct ob3_wall_loader_t ob3_wall_loaders[] = {
    {
        "bsetbg",
        "bsetbg -full %s"
    },
    {
        "Esetroot",
        "Esetroot -scale %s"
    },
    {
        "wmsetbg",
        "wmsetbg -s -S %s"
    },
    {
        "xsetbg",
        "xsetbg -fillscreen %s"
    },
    {
        "xli",
        "xli -fillscreen -onroot -quiet %s"
    },
    {
        "qiv",
        "qiv --root_s %s"
    },
    {
        "xv",
        "xv -max -smooth -root -quit %s"
    },
    {
        NULL,
        NULL
    }
};

void ob3_init(gint argc, gchar **argv);
void ob3_exit(gint level);

void ob3_config_load(void);

void ob3_wall_menu_create(void);
void ob3_wall_use(const gchar *file);

void ob3_usage(void);
void ob3_version(void);

gchar *ob3_wall_home, *ob3_wall_rc, *ob3_wall_cmd, *ob3_wall_path,
      *ob3_wall_file;

GSList *ob3_wall_list, *ob3_wall_dirs;

gint main(gint argc, gchar **argv)
{
    ob3_init(argc, argv); /* setup variables, slist */

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

    if(argc == 1)
        ob3_wall_menu_create();
    else
        ob3_wall_use(argv[1]);

    ob3_exit(0);

    exit(0); /* not reached */
}

/* returns the full path of the previously selected wallpaper */
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

gchar *ob3_wall_cmd_setup(void)
{
    gint i;

    for(i = 0; ob3_wall_loaders[i].name; i++) {
        gchar *p;

        if((p = g_find_program_in_path(ob3_wall_loaders[i].name))) {
            g_free(p);

            return(g_strdup(ob3_wall_loaders[i].cmd));
        }
    }

    return(NULL);
}

void ob3_init(gint argc, gchar **argv)
{
    g_set_prgname(argv[0]);

    ob3_pipemenu_startup();

    parse_paths_startup();

    /* ~/.config/ob3_wall/ */
    ob3_wall_home  = g_build_filename(parse_xdg_config_home_path(),
                                      "ob3_wall", NULL);

    /* ~/.config/ob3_wall/wall (symlink used for setting up new wallpaper) */
    ob3_wall_path  = g_build_filename(ob3_wall_home, "wall", NULL);

    /* path to wallpaper (used for setting) */
    ob3_wall_file  = ob3_readlink(ob3_wall_path);

    /* ~/.config/ob3_wall/rc.xml */
    ob3_wall_rc    = g_build_filename(ob3_wall_home, "rc.xml", NULL);

    ob3_wall_cmd   = NULL;

    ob3_wall_list  = NULL;
    ob3_wall_dirs  = NULL;

    if(!parse_mkdir_path(parse_xdg_config_home_path(), 0755))
        ob3_exit(1);

    if(!parse_mkdir(ob3_wall_home, 0755))
        ob3_exit(1);

    ob3_config_load();

    /* 'command = ...' not in the config file, try to locate a command */
    if(!ob3_wall_cmd)
        ob3_wall_cmd = ob3_wall_cmd_setup();
}

void ob3_wall_free(struct ob3_wall_t *wall)
{
    g_return_if_fail(wall != NULL);

    g_free(wall->path);
    g_free(wall->name);

    g_free(wall);
}

void ob3_exit(gint level)
{
    g_free(ob3_wall_home);
    g_free(ob3_wall_rc);
    g_free(ob3_wall_path);
    g_free(ob3_wall_file);
    g_free(ob3_wall_cmd);

    g_slist_foreach(ob3_wall_list, (GFunc) ob3_wall_free, NULL);
    g_slist_free(ob3_wall_list);

    g_slist_foreach(ob3_wall_dirs, (GFunc) g_free, NULL);
    g_slist_free(ob3_wall_dirs);

    parse_paths_shutdown();

    ob3_pipemenu_display("UTF-8");

    ob3_pipemenu_shutdown();

    exit(level);
}

/* leaves the first %s intact, everything else gets escaped */
gchar *ob3_escape_command_format(const gchar *str)
{
    GString *string;

    g_return_val_if_fail(str != NULL, NULL);

    string = g_string_new(NULL);

    {
        const guchar *p = (guchar *) str;
        gboolean found = FALSE;

        while(*p) {
            if(*p == '%') {
                if(!found && p[1] == 's')
                    found = TRUE;
                else
                    g_string_append_c(string, *p);
            }

            g_string_append_c(string, *p++);
        }
    }

    return(g_string_free(string, FALSE));
}

/* used for the initial config creation only */
void ob3_config_save(void)
{
    FILE *fp;

    if(!(fp = fopen(ob3_wall_rc, "w"))) {
        g_critical("unable to open %s: %s", ob3_wall_rc, G_ERROR);
        ob3_exit(1);
    }

    if(!ob3_wall_cmd)
        ob3_wall_cmd = ob3_wall_cmd_setup();

    fprintf(fp, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n");

    fprintf(fp, "<ob3_wall_config ");
    fprintf(fp, "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n");

    fprintf(fp, "  <!-- command to set wallpaper (must contain one %%s, ");
    fprintf(fp, "file substitution) -->\n");

    if(!ob3_wall_cmd)
        fprintf(fp, "<!--\n");

    fprintf(fp, "  <command>%s</command>\n",
            (ob3_wall_cmd) ? ob3_wall_cmd : "bsetbg -full %%s");

    if(!ob3_wall_cmd)
        fprintf(fp, "-->\n");

    fprintf(fp, "  <!-- directories to scan -->\n");

    {
        GSList *p;

        for(p = parse_xdg_data_dir_paths(); p; p = g_slist_next(p))
            fprintf(fp, "  <dir>%s/wallpapers</dir>\n", (gchar *) p->data);
    }

    fprintf(fp, "</ob3_wall_config>\n");

    fclose(fp);
}

void ob3_config_load(void)
{
    xmlDocPtr doc;
    xmlNodePtr node;

    if(!IS_FILE(ob3_wall_rc)) {
        ob3_config_save();
        return;
    }

    if(parse_load(ob3_wall_rc, "ob3_wall_config", &doc, &node)) {
        xmlNodePtr n;

        node = node->children;

        if((n = parse_find_node("command", node))) {
            gchar *p = parse_string(doc, n);

            if(p && p[0] && strstr(p, "%s")) {
                gchar *s = parse_expand_tilde(p);
                ob3_wall_cmd = ob3_escape_command_format(s);
                g_free(s);
            } else
                g_warning("invalid wallpaper command \"%s\"", p);

            g_free(p);
        }

        while((n = parse_find_node("dir", node))) {
            gchar *p = parse_string(doc, n);
            if(p && p[0])
                ob3_wall_dirs = g_slist_append(ob3_wall_dirs,
                                               parse_expand_tilde(p));
            g_free(p);

            node = n->next;
        }
    }

    parse_close(doc);
}

gboolean ob3_wall_is_likely(const gchar *name)
{
    g_return_val_if_fail(name != NULL, FALSE);

    if(name[0] == '.')
        return(FALSE);

    if(strstr(name, "README"))
        return(FALSE);

    {
        gchar *ext;

        if(!(ext = strrchr(name, '.')) || !g_ascii_strcasecmp(ext, ".txt"))
            return(FALSE);
    }

    return(TRUE);
}

gint ob3_wall_path_cmp(struct ob3_wall_t *a, struct ob3_wall_t *b)
{
    return(strcmp(a->path, b->path));
}

gint ob3_wall_name_cmp(struct ob3_wall_t *a, struct ob3_wall_t *b)
{
    return(strcmp(a->name, b->name));
}

void ob3_process_wall_dir(const gchar *dir)
{
    const gchar *p;

    GDir *dp;

    g_return_if_fail(dir != NULL);

    if(IS_DIR(dir) == FALSE)
        return;

    if(!(dp = g_dir_open(dir, 0, NULL))) {
        g_warning("unable to open %s: %s", dir, G_ERROR);
        return;
    }

    while((p = g_dir_read_name(dp))) {
        gchar *path = g_build_filename(dir, p, NULL);

        /* IS_FILE() or check image extentions? */
        if(IS_FILE(path) && ob3_wall_is_likely(p)) {
            struct ob3_wall_t *wall;

            wall       = g_new(struct ob3_wall_t, 1);
            wall->path = path;
            wall->name = g_path_get_basename(path);

            /* don't add dupes */
            if(!g_slist_find_custom(ob3_wall_list, wall,
                                   (GCompareFunc) ob3_wall_path_cmp))
                ob3_wall_list = g_slist_insert_sorted(ob3_wall_list, wall,
                                    (GCompareFunc) ob3_wall_name_cmp);
            else
                ob3_wall_free(wall);
        } else
            g_free(path);
    }

    g_dir_close(dp);
}

/* displays openbox pipe-menu xml output */
void ob3_wall_menu_create(void)
{
    GSList *p;

    if(!ob3_wall_cmd) {
        ob3_pipemenu_item_add(NULL, "No Image Loader Found in $PATH", NULL);
        g_critical("no image loader found in $PATH");
        ob3_exit(1);
    }

    if(!ob3_wall_dirs) {
        for(p = parse_xdg_data_dir_paths(); p; p = g_slist_next(p)){
            gchar *path = g_build_filename(p->data, "wallpapers", NULL);
            ob3_process_wall_dir(path);
            g_free(path);
        }
    } else
        g_slist_foreach(ob3_wall_dirs, (GFunc) ob3_process_wall_dir, NULL);

    if(ob3_wall_list) {
        for(p = ob3_wall_list; p; p = g_slist_next(p)) {
            struct ob3_wall_t *wall = p->data;
            gchar *label, *action;

            if(!wall || !wall->name || !wall->path)
                continue;

            if(ob3_wall_file && !strcmp(wall->path, ob3_wall_file))
                label = g_strconcat(wall->name, " <-", NULL);
            else
                label = g_strdup(wall->name);

            {
                gchar *s = g_shell_quote(wall->path);
                action = g_strconcat(g_get_prgname(), " ", s, NULL);
                g_free(s);
            }

            ob3_pipemenu_item_add(NULL, label, action);

            g_free(label);
            g_free(action);
        }
    } else
        ob3_pipemenu_item_add(NULL, "No Wallpaper Found", NULL);
}

/* create the ~/.config/ob3_wall/wall symlink */
void ob3_symlink(const gchar *wall, const gchar *path)
{
    g_return_if_fail(wall != NULL);
    g_return_if_fail(path != NULL);

    if(symlink(wall, path) == -1) {
        g_critical("unable to symlink %s to %s: %s", wall, path, G_ERROR);
        ob3_exit(1);
    }
}

/* remove the ~/.config/ob3_wall/wall symlink */
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

void ob3_wall_use(const gchar *file)
{
    gchar *command, path[PATH_MAX];

    GError *error = NULL;

    gboolean reuse = FALSE;

    g_return_if_fail(file != NULL);

    /* ob3_wall -: use symlink for wallpaper */
    if(!g_ascii_strcasecmp(file, "-")) {
        reuse = TRUE;

        if(!(file = ob3_wall_file)) {
           g_critical("previous wallpaper selection unavailable");
           ob3_exit(1);
        }
    }

    if(!IS_FILE(file)) {
        g_critical("\"%s\" does not exist", file);
        ob3_exit(1);
    }

    if(!ob3_wall_cmd) {
        g_critical("no image loader found in $PATH");
        ob3_exit(1);
    }

    {
        gchar *p = g_shell_quote(file);
        command = g_strdup_printf(ob3_wall_cmd, p);
        g_free(p);
    }

    if(!g_spawn_command_line_async(command, &error)) {
        g_warning("%s", error->message);
        g_error_free(error);
        g_free(command);
        return;
    }

    g_free(command);

    /* nothing else to do */
    if(reuse)
      return;

    /* remove ~/.config/ob3_wall/wall symlink */
    ob3_unlink(ob3_wall_path);

    /* resolve relative paths for symlink creation */
    if(!g_path_is_absolute(file))
        if(!realpath(file, path))
            ob3_exit(1);

    ob3_symlink(path, ob3_wall_path);
}

void ob3_usage(void)
{
    const gchar *prog = g_get_prgname();

    ob3_version();

    fprintf(stderr, "\n");
    fprintf(stderr, "Usage: %s <wallpaper|->\n\n", prog);

    fprintf(stderr, "  Examples:\n");
    fprintf(stderr, "    # create menu\n");
    fprintf(stderr, "    %s\n", prog);
    fprintf(stderr, "    # use specified wallpaper\n");
    fprintf(stderr, "    %s /path/to/wallpaper.png\n", prog);
    fprintf(stderr, "    # use previously configured wallpaper (~/.xinitrc)\n");
    fprintf(stderr, "    %s -\n\n", prog);

    fprintf(stderr, "  Usage:\n");
    fprintf(stderr, "    ~/.config/openbox/menu.xml:\n");
    fprintf(stderr, "      <menu id=\"ob3_wall\" label=\"Wallpaper\" ");
    fprintf(stderr, "execute=\"%s\" />\n", prog);
}

void ob3_version(void)
{
    fprintf(stderr, "%s v%s (%s)\n", PROGRAM, VERSION, URL);
}

/*
 * --- Changelog --------------------------------------------------------------
 *
 *  0.01 - 2003/10/19:
 *    initial release.
 *
 *  0.02 - 2003/10/21:
 *    relocated configuration to ~/.config/ob3_wall.
 *    denote currently used wallpaper with an arrow.
 *    include openbox/parse.h for XDG related functions.
 *    use XDG data dirs as defaults, empty when user-defined dirs are found.
 *    remove glib.h include (already included with openbox/parser.h).
 *
 *  0.03 - 2003/10/22:
 *    added some generic checks for image types. ignore README, *.txt or 
 *      files with no extentions.
 *    if no 'command' is specified in the config file, $PATH will be scanned
 *      for: bsetbg, Esetroot, wmsetbg, xsetbg, xli, qiv, and xv. if nothing
 *      is found, an error will be displayed and ob3_wall will exit.
 *    add recursive mkdir for ~/.config (or $XDG_CONFIG_HOME).
 *    fix improper g_return_[val]if_fail() usage.
 *
 *  0.04 - 2003/11/04:
 *    require openbox 3.0. remove ob3_mkdir* and use parse_mkdir*, dupe check.
 *    make ob3_readlink() return an allocated buffer.
 *    move parse_paths_shutdown() to ob3_exit().
 *    use system paths if no custom dirs have been configured (in rc), check
 *      for dupes before adding wallpaper to the list.
 *    updated ob3_string_to_xml_safe() to only encode <>&'" and non-printable
 *      characters.
 *    use g_shell_quote() on paths.
 *    use g_warning() instead of ob3_error().
 *    use g_path_get_basename() instead of deprecated g_basename().
 *    use parse_expand_tidle() instead of ob3_expand_tilde().
 *    do tilde expansion on 'command' (config).
 *    other cleanups.
 *
 *  0.05 - 2003/11/06:
 *    convert config to xml, renamed to rc.xml.
 *
 *  0.06 - 2003/11/15:
 *    add in pipe-menu helpers, use xml functions to print the created menu.
 *      removed ob3_string_to_xml_safe().
 *    use g_critical() in appropriate situations.
 *
 *  0.07 - 2004/11/08:
 *    misc cleanups.
 *
 *  0.07.1 - 2006/08/27:
 *    fix libxml signedness warnings
 *
 *  0.08 - 2006/10/25:
 *    resolve relative paths when creating the symlink
 *
 *  0.08.1 - 2006/10/31:
 *    don't remove symlink on reuse last
 *
 * --- Changelog --------------------------------------------------------------
 */
