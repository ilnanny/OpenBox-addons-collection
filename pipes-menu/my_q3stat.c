/*
 * my_q3stat.c-v1.7:
 *   my_q3stat is a simple program that will display the status of a q3a server.
 *
 * Compiling:
 *   gcc -Wall -O2 -o my_q3stat my_q3stat.c
 *
 *     -D_DEBUG - enables debugging
 *
 * Usage:
 *   my_q3stat midwestmayhem.com
 *   my_q3stat -c midwestmayhem.com:27960
 *   my_q3stat -g gamename -g mapname -g version 207.44.182.28 207.44.132.85
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
#include <ctype.h>
#include <signal.h>
#include <values.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

#ifdef __sun__
extern char *optarg;
extern int optind;
extern int getopt ();
#else
#include <getopt.h>
#endif

#define VERSION			"1.7"
#define PROGRAM			"my_q3stat"
#define URL			"http://www.gozer.org/my_stuff/c/c/my_q3stat.c"

#define Q3A_MAX_NAME_LEN	(64 + 1)	/* 32? */
#define Q3A_PORT		27960

#define Q3A_STATUS_SEND		"\377\377\377\377getstatus"
#define Q3A_STATUS_READ		"\377\377\377\377statusResponse"

#define TIMEOUT			30

#ifndef isdigit
#define isdigit(c)		(((c) >= '0') && ((c) <= '9'))
#endif

struct q3a_player {
	char	*name;
	int	ping;
	int	score;
};

struct q3a_var {
	char    *name;
	char    *value;
};

struct q3a {
	int	sv_players;
	struct	q3a_var **var;
	struct	q3a_player **player;
};

struct q3a_opt {
	char	*host;
	int	port;
	int	timeout;
	int	compact;
	int	show_vars;
	char    **var;
};

#define MAX_Q3A_TYPES 10
char *q3a_gametypes[MAX_Q3A_TYPES] = {
	"FFA",		/* 0 = Free for All */
	"1v1",		/* 1 = Tournament */
	NULL,		/* 2 = Single Player */
	"TDM",		/* 3 = Team Deathmatch */
	"CTF",		/* 4 = Capture the Flag */
	"1FCTF",	/* 5 = One Flag Capture the Flag */
	"OVR",		/* 6 = Overload */
	"HRV",		/* 7 = Harvester */
	" mod ",	/* 8+ is usually a client-side mod */
	NULL
};

#define MAX_Q3A_OSP_TYPES 7
static char *q3a_osp_gametypes[MAX_Q3A_OSP_TYPES] = {
	"FFA",		/* 0 = Free for All */
	"1v1",		/* 1 = Tournament */
	"FFA Comp",	/* 2 = FFA, Competition */
	"TDM",		/* 3 = Team Deathmatch */
	"CTF",		/* 4 = Capture the Flag */
	"Clan Arena",	/* 5 = Clan Arena */
	"Custom OSP",	/* 6+ is usually a custom OSP setting */
};

#define MAX_Q3A_UT2_TYPES 9
char *q3a_ut2_gametypes[MAX_Q3A_UT2_TYPES] = {
	"FFA",		/* 0 = Free for All */
	"FFA",		/* 1 = Free for All */
	"FFA",		/* 2 = Free for All */
	"TDM",		/* 3 = Team Deathmatch */
	"TS",		/* 4 = Team Survivor */
	"FTL",		/* 5 = Follow the Leader */
	"CAH",		/* 6 = Capture & Hold */
	"CTF",		/* 7 = Capture the Flag */
	NULL		/* 8+ ?? */
};

#define MAX_Q3A_UT3_TYPES 10
char *q3a_ut3_gametypes[MAX_Q3A_UT3_TYPES] = {
	"FFA",		/* 0 = Free for All */
	"FFA",		/* 1 = Free for All */
	"FFA",		/* 2 = Free for All */
	"TDM",		/* 3 = Team Deathmatch */
	"TS",		/* 4 = Team Survivor */
	"FTL",		/* 5 = Follow the Leader */
	"CAH",		/* 6 = Capture & Hold */
	"CTF",		/* 7 = Capture the Flag */
	"Bomb",		/* 8 = Bomb/Defuse */
	NULL		/* 9+ ?? */
};

#define MAX_Q3A_TRUECOMBAT_TYPES 11
char *q3a_truecombat_gametypes[MAX_Q3A_TRUECOMBAT_TYPES] = {
	"FFA",		/* 0 = Free for All */
	NULL,		/* 1 = ? */
	NULL,		/* 2 = ? */
	"Survivor",	/* 3 = Survivor */
	"TDM",		/* 4 = Team Deathmatch */
	"CTF",		/* 5 = Capture the Flag */
	"TS",		/* 6 = Team Survivor */
	NULL,		/* 7 = ? */
	"CAH",		/* 8 = Capture & Hold */
	"KOTH",		/* 9 = King of the hill */
	NULL		/* 10+ ?? */
};

#define MAX_Q3A_THREEWAVE_TYPES 12
static char *q3a_threewave_gametypes[MAX_Q3A_THREEWAVE_TYPES] = {
	"FFA",		/* 0  - Free For All */
	"1v1",		/* 1  - Tournament */
	NULL,		/* 2  - Single Player (invalid, don't use this) */
	"TDM",		/* 3  - Team Deathmatch */
	"ThreeWave CTF",	/* 4  - ThreeWave CTF */
	"One flag CTF",	/* 5  - One flag CTF  (invalid, don't use this) */
	"Obelisk",	/* 6  - Obelisk       (invalid, don't use this) */
	"Harvester",	/* 7  - Harvester     (invalid, don't use this) */
	"Portal",	/* 8  - Portal        (invalid, don't use this) */
	"CaptureStrike",	/* 9  - CaptureStrike */
	"Classic CTF",	/* 10 - Classic CTF */
	NULL		/* 11+ ??? */
};

#define MAX_Q3A_TRIBALCTF_TYPES 10
static char *q3a_tribalctf_gametypes[MAX_Q3A_TRIBALCTF_TYPES] = {
	NULL,		/* 0 - Unknown */
	NULL,		/* 1 - Unknown */
	NULL,		/* 2 - Unknown */
	NULL,		/* 3 - Unknown */
	NULL,		/* 4 - Unknown */
	NULL,		/* 5 - Unknown */
	"Freestyle",	/* 6 - Freestyle */
	"Fixed",	/* 7 - Fixed */
	"Roulette",	/* 8 - Roulette */
	NULL		/* 9+ ??? */
};

#define MAX_Q3A_SEALS_TYPES 5
char *q3a_seals_gametypes[MAX_Q3A_SEALS_TYPES] = {
	NULL,		/* 0 = devmode */
	NULL,		/* 1 = invalid */
	NULL,		/* 2 = invalid */
	"Operations",	/* 3 = Team Deathmatch */
	NULL		/* 4+ invalid */
};

#define MAX_Q3A_AFTERWARDS_TYPES 3
static char *q3a_afterwards_gametypes[MAX_Q3A_AFTERWARDS_TYPES] = {
	"Tactical",	/* 0 = Tactical */
	"FFA",		/* 1 = Deatchmatch */
	NULL,		/* 2+ ?? */
};

#define MAX_Q3A_ARENA_TYPES 10
// Not sure what the proper types are, but 99% of them are a game
// type of 8.  Just call them all "arena"
static char *q3a_arena_gametypes[MAX_Q3A_ARENA_TYPES] = {
	"arena",	/* 0 = Arena */
	"arena",	/* 1 = Arena */
	"arena",	/* 2 = Arena */
	"arena",	/* 3 = Arena */
	"arena",	/* 4 = Arena */
	"arena",	/* 5 = Arena */
	"arena",	/* 6 = Arena */
	"arena",	/* 7 = Arena */
	"arena",	/* 8 = Arena */
	NULL
};

#define MAX_Q3A_CPMA_TYPES 7
static char *q3a_cpma_gametypes[MAX_Q3A_CPMA_TYPES] = {
	"FFA",		/* 0 = Free for All */
	"1v1",		/* 1 = Tournament */
	NULL,		/* 2 = Single Player */
	"TDM",		/* 3 = Team Deathmatch */
	"CTF",		/* 4 = Capture the Flag */
	"Clan Arena",	/* 5 = Clan Arena */
	NULL
};

#define MAX_Q3A_Q3F_TYPES 7
static char *q3a_q3f_gametypes[MAX_Q3A_Q3F_TYPES] = {
	"q3f",		/* 0 = Arena */
	"q3f",		/* 1 = Arena */
	"q3f",		/* 2 = Arena */
	"q3f",		/* 3 = Arena */
	"q3f",		/* 4 = Arena */
	"q3f",		/* 5 = Arena */
	NULL
};

#define MAX_Q3A_WQ3_TYPES 7
static char *q3a_wq3_gametypes[MAX_Q3A_WQ3_TYPES] = {
	"FFA",
	"Duel",
	NULL,
	"TDM",
	"Round Teamplay",
	"Bank Robbery",
	NULL
};

struct q3a_gametype_s {
	char *mod;
	char **gametypes;
	int number;
};

struct q3a_gametype_s q3a_gametype_map[] = {
	{
		"baseq3",
		q3a_gametypes,
		MAX_Q3A_TYPES
	},
	{
		"osp",
		q3a_osp_gametypes,
		MAX_Q3A_OSP_TYPES
	},
	{
		"q3ut2",
		q3a_ut2_gametypes,
		MAX_Q3A_UT2_TYPES
	},
	{
		"q3ut3",
		q3a_ut3_gametypes,
		MAX_Q3A_UT3_TYPES
	},
	{
		"threewave",
		q3a_threewave_gametypes,
		MAX_Q3A_THREEWAVE_TYPES
	},
	{
		"seals",
		q3a_seals_gametypes,
		MAX_Q3A_SEALS_TYPES
	},
	{
		"TribalCTF",
		q3a_tribalctf_gametypes,
		MAX_Q3A_TRIBALCTF_TYPES
	},
	{
		"missionpack",
		q3a_gametypes,
		MAX_Q3A_TYPES
	},
	{
		"generations",
		q3a_gametypes,
		MAX_Q3A_TYPES
	},
	{
		"q3tc045",
		q3a_truecombat_gametypes,
		MAX_Q3A_TRUECOMBAT_TYPES
	},
	{
		"freeze",
		q3a_gametypes,
		MAX_Q3A_TYPES
	},
	{
		"afterwards",
		q3a_afterwards_gametypes,
		MAX_Q3A_AFTERWARDS_TYPES
	},
	{
		"cpma",
		q3a_cpma_gametypes,
		MAX_Q3A_CPMA_TYPES
	},
	{
		"arena",
		q3a_arena_gametypes,
		MAX_Q3A_ARENA_TYPES
	},
	{
		"instaunlagged",
		q3a_gametypes,
		MAX_Q3A_TYPES
	},
	{
		"instagibplus",
		q3a_gametypes,
		MAX_Q3A_TYPES
	},
	{
		"beryllium",
		q3a_gametypes,
		MAX_Q3A_TYPES
	},
	{
		"excessive",
		q3a_gametypes,
		MAX_Q3A_TYPES
	},
	{
		"q3f",
		q3a_q3f_gametypes,
		MAX_Q3A_Q3F_TYPES
	},
	{
		"q3f2",
		q3a_q3f_gametypes,
		MAX_Q3A_Q3F_TYPES
	},
	{
		"westernq3",
		q3a_wq3_gametypes,
		MAX_Q3A_WQ3_TYPES
	},
	{
		NULL,
		NULL,
		0
	}
};

void q3a_get_status(struct q3a_opt *q_opt);
struct q3a *q3a_connect(struct q3a_opt *);
struct q3a *q3a_process(struct q3a_opt *q_opt,
			const char *message,
			int message_len);
char *q3a_game_type(const char *gamename, int type);
char *q3a_get_var(struct q3a *q, const char *str);
char *q3a_clean_name(const char *name);
void q3a_usage(void);
int q3a_isdigit(char *str);
int q3a_is_fd(int fd);
void q3a_free(struct q3a *q);
void q3a_show_var(const char *name, const char *value);
void q3a_debug(const char *, ...);

#define DEBUG q3a_debug

char *g_strdup(const char *str);

void g_free(void *mem);
void *g_malloc(unsigned long n_bytes);
void *g_realloc(void *mem, unsigned long n_bytes);

void g_error(const char *fmt, ...);

char **g_strsplit(const char *str_array, const char *delimiter, int max_tokens);
void g_strfreev(char **str_array);

char *prog;

int sockfd;

void SIG_ALRM()
{
	DEBUG("SIG_ALRM()");

	if(close(sockfd) == -1) {
		fprintf(stderr, "%s: close: %s\n", prog, strerror(errno));
		exit(1);
	}

	signal(SIGALRM, SIG_ALRM);
}

int main(int argc, char **argv)
{
	int option, i;

	unsigned int size;

	struct q3a_opt q_opt;

	q_opt.timeout   = TIMEOUT;
	q_opt.compact   = 0;
	q_opt.show_vars = 0;

	signal(SIGALRM, SIG_ALRM);

	prog = argv[0];

	size = sizeof(char *);
	q_opt.var = g_malloc(size);

	i = 0;

	DEBUG("main(): processing command line options");

	while((option = getopt(argc, argv, "cg:st:")) != EOF) {
		switch(option) {
			case 'c':
				q_opt.compact = 1;
				break;
			case 'g':
				q_opt.compact = 1;

				q_opt.var[i++] = g_strdup(optarg);

				size += sizeof(char *);
				q_opt.var = g_realloc(q_opt.var, size);

				break;
			case 's':
				q_opt.show_vars = 1;
				q_opt.compact = 1;
				break;
			case 't':
				if(!q3a_isdigit(optarg)) {
					q3a_usage();
					exit(1);
				}

				q_opt.timeout = atoi(optarg);

				/* sane timeout value */
				if(q_opt.timeout < 1 || q_opt.timeout > 60)
					q_opt.timeout = TIMEOUT;

				break;
			default:
				q3a_usage();
				exit(1);
		}
	}

	q_opt.var[i] = NULL;

	/* no host specified */
	if(optind == argc) {
		q3a_usage();
		exit(1);
	}

	while(optind < argc) {
		char **s;

		/* reset to default */
		q_opt.host = NULL;
		q_opt.port = Q3A_PORT;

		if((s = g_strsplit(argv[optind++], ":", 2))) {
			q_opt.host = g_strdup(s[0]);

			if(s[1] != NULL) {
				if(q3a_isdigit(s[1])) {
					q_opt.port = atoi(s[1]);
				} else {
					g_strfreev(s);
					continue;
				}
			}

			g_strfreev(s);
		}

#ifdef _DEBUG
	DEBUG("main(): q_opt.host      = %s", q_opt.host);
	DEBUG("main(): q_opt.port      = %d", q_opt.port);
	DEBUG("main(): q_opt.timeout   = %d", q_opt.timeout);
	DEBUG("main(): q_opt.compact   = %d", q_opt.compact);
	DEBUG("main(): q_opt.show_vars = %d", q_opt.show_vars);

	for(i = 0; q_opt.var[i] != NULL; i++)
		DEBUG("main(): q_opt.var[%d]   = %s", i, q_opt.var[i]);
#endif

		q3a_get_status(&q_opt);

		g_free(q_opt.host);

		/* newline between each server's info if not compact */
		if(!q_opt.compact && optind + 1 <= argc)
			printf("\n");
	}

	for(i = 0; q_opt.var[i] != NULL; i++)
		g_free(q_opt.var[i]);

	g_free(q_opt.var);

	exit(0);
}

void q3a_get_status(struct q3a_opt *q_opt)
{
	int i;
	int sv_maxc = 0, sv_priv = 0;

	char *p, *gametype = NULL;

	struct q3a *q;

	DEBUG("q3a_get_status(%s, %d)", q_opt->host, q_opt->port);

	/* no or invalid data returned */
	if((q = q3a_connect(q_opt)) == NULL)
		return;

	printf("%s:%d: ", q_opt->host, q_opt->port);

	if((p = q3a_get_var(q, "version"))) {
		char **s;

		if((s = g_strsplit(p, " ", 3))) {
			printf("%s-%s", s[0], s[1]);

			g_strfreev(s);
		}

		/* uses punkbuster */
		if((p = q3a_get_var(q, "sv_punkbuster")))
			if(atoi(p) == 1)
				printf("-PB");

		printf(": ");
	}

	/* baseq3, q3ut2 */
	if((p = q3a_get_var(q, "gamename"))) {
		char *s;

		if((s = q3a_get_var(q, "g_gametype")))
			gametype = q3a_game_type(p, atoi(s));

		printf("%s", p);
	}


	if((p = q3a_get_var(q, "g_modversion")))
		printf("-%s", p);

	printf(": ");

	/* TS, CTF, CAH */
	if(gametype)
		printf("%s ", gametype);

	/* ut_docks */
	if((p = q3a_get_var(q, "mapname")))
		printf("(%s): ", p);

	if((p = q3a_get_var(q, "sv_maxclients")))
		sv_maxc = atoi(p);

	if((p = q3a_get_var(q, "sv_privateclients")))
		sv_priv = atoi(p);

	printf("%2d/%2d", q->sv_players, sv_maxc);

	if(sv_priv)
		printf(" (-%d)", sv_priv);

	printf("\n");

	/* show specified variables */
	for(i = 0; q_opt->var[i] != NULL; i++)
		if((p = q3a_get_var(q, q_opt->var[i])))
			q3a_show_var(q_opt->var[i], p);

	/* compact mode or empty server */
	if(q_opt->compact || q->sv_players == 0) {
		if(q_opt->show_vars) {
			printf("\n  Server Variables:\n");

			for(i = 0; q->var[i] != NULL; i++)
				q3a_show_var(q->var[i]->name,
					q->var[i]->value);
		}

		q3a_free(q);

		return;
	}

	printf("\n     Name                               Ping    Score\n");

	for(i = 0; q->player[i] != NULL; i++)
		printf(" %2d. %-32s   %-3d     %-3d\n", i + 1,
			q->player[i]->name, q->player[i]->ping,
			q->player[i]->score);

	q3a_free(q);
}

/* connect to the host and receive the buffer from the server for parsing */
struct q3a *q3a_connect(struct q3a_opt *q_opt)
{
	int bytes;

	char response[16384];

	struct hostent *he;
	struct sockaddr_in their_addr;

	DEBUG("q3a_connect(%s, %d)", q_opt->host, q_opt->port);

	alarm(0);
	alarm(q_opt->timeout);

	if((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
		fprintf(stderr, "%s: %s:%d: %s\n",
			prog, q_opt->host, q_opt->port, strerror(errno));
		exit(1);
	}

	DEBUG("q3a_connect(): gethostbyname(%s)", q_opt->host);

	if((he = gethostbyname(q_opt->host)) == NULL) {
		fprintf(stderr, "%s: %s:%d: %s\n",
			prog, q_opt->host, q_opt->port, hstrerror(h_errno));
		return((struct q3a *) NULL);
	}

	their_addr.sin_family = AF_INET;
	their_addr.sin_port = htons(q_opt->port);
	their_addr.sin_addr = *((struct in_addr *)he->h_addr);

	bzero(&(their_addr.sin_zero), 8);

	DEBUG("q3a_connect(): connect()");

	if(connect(sockfd, (struct sockaddr *)&their_addr,
		sizeof(struct sockaddr)) == -1) {

		fprintf(stderr, "%s: %s:%d: %s\n",
			prog, q_opt->host, q_opt->port, strerror(errno));
		return((struct q3a *) NULL);
	}

	DEBUG("q3a_connect(): send()");

	if(send(sockfd, Q3A_STATUS_SEND, strlen(Q3A_STATUS_SEND), 0) == -1) {
		fprintf(stderr, "%s: %s:%d: %s\n",
			prog, q_opt->host, q_opt->port, strerror(errno));
		return((struct q3a *) NULL);
	}

	DEBUG("q3a_connect(): read()");

	if((bytes = read(sockfd, response, sizeof(response))) == -1) {
		if(!q3a_is_fd(sockfd)) /* likely the connection timed out */
			errno = ETIMEDOUT;

		fprintf(stderr, "%s: %s:%d: %s\n",
			prog, q_opt->host, q_opt->port, strerror(errno));

		return((struct q3a *) NULL);
	}

	response[bytes] = '\0';

	if(close(sockfd) == -1) {
		fprintf(stderr, "%s: %s:%d: %s\n",
			prog, q_opt->host, q_opt->port, strerror(errno));
		exit(1);
	}

	alarm(0);

	return(q3a_process(q_opt, response, bytes));
}

/* parses the output from the received message */
struct q3a *q3a_process(struct q3a_opt *q_opt,
			const char *message,
			int message_len)
{
	int i = 0, ct;

	unsigned int size;

	char **s, *status = NULL, *vars = NULL, *players = NULL;

	struct q3a *q;

	DEBUG("q3a_process()");

	if(message == NULL) {
		fprintf(stderr, "%s: %s:%d: no data returned\n",
			prog, q_opt->host, q_opt->port);
		return((struct q3a *) NULL);
	}

	DEBUG("q3a_process(): checking for valid response");

	/* ÿÿÿÿstatusResponse\n\var1\val1\var2\varl2\n13 98 "P1"\n3 76 "P2"\n */
	if((s = g_strsplit(message, "\n", 3))) {
		if((status = s[0]))
			if((vars = s[1]))
				players = s[2];

		g_free(s);
	}

	if(status == NULL || vars == NULL || strcmp(status, Q3A_STATUS_READ)) {
		fprintf(stderr, "%s: %s:%d: invalid data returned\n",
			prog, q_opt->host, q_opt->port);

		g_free(status);
		g_free(vars);
		g_free(players);

		return((struct q3a *) NULL);
	}

	g_free(status);

	DEBUG("q3a_process(): valid response found");

	q = g_malloc(sizeof(struct q3a));

	q->sv_players = 0;

	q->var        = NULL;
	q->player     = NULL;

	DEBUG("q3a_process(): processing variables");

	size = sizeof(struct q3a_var *);
	q->var = g_malloc(size);

	q->var[0] = NULL;

	ct = 0;

	if(vars != NULL && (s = g_strsplit(vars + 1, "\\", 0))) {
		for(i = 0; s[i] != NULL; i++) {
			if((i % 2) == 0) {
				q->var[ct] = g_malloc(sizeof(struct q3a_var));

				q->var[ct]->name  = g_strdup(s[i]);
			} else {
				q->var[ct]->value = g_strdup(s[i]);

				DEBUG("q3a_process(): var[%2d]: %s, '%s'",
					ct,
					q->var[ct]->name,
					q->var[ct]->value);

				ct++;

				size += sizeof(struct q3a_var *);
				q->var = g_realloc(q->var, size);
			}
		}

		g_strfreev(s);
	}

	g_free(vars);

	q->var[ct] = NULL;

	DEBUG("q3a_process(): %d variables found", ct);

	/* make sure there's sane data */
	if(ct < 1) {
		g_free(players);
		q3a_free(q);
		return((struct q3a *) NULL);
	}

	DEBUG("q3a_process(): processing players");

	size = sizeof(struct q3a_player *);
	q->player = g_malloc(size);

	q->player[0] = NULL;

	ct = 0;

	/* handle players */
	if(players != NULL && (s = g_strsplit(players, "\n", 0))) {
		for(i = 0; s[i] != NULL; i++) {
			char name[Q3A_MAX_NAME_LEN];
			int score, ping;

			if((sscanf(s[i], "%d %d \"%64[^\"\n]",
				&score, &ping, name)) != 3)
					continue;

			q->player[ct] = g_malloc(sizeof(struct q3a_player));

			q->player[ct]->name  = q3a_clean_name(name);
			q->player[ct]->ping  = ping;
			q->player[ct]->score = score;

			DEBUG("q3a_process(): player[%2d]: '%s', %d, %d",
				ct,
				q->player[ct]->name,
				q->player[ct]->ping,
				q->player[ct]->score);

			ct++;

			size += sizeof(struct q3a_player *);
			q->player = g_realloc(q->player, size);
		}

		g_strfreev(s);
	}

	g_free(players);

	q->player[ct] = NULL;

	DEBUG("q3a_process(): %d players found", ct);

	q->sv_players = ct--;

	return(q);
}

/* returns the game type (CTF, FTL) for the gamename (baseq3, q3ut2) */
char *q3a_game_type(const char *gamename, int type)
{
	int i;

	static char buf[10];

	/* DEBUG("q3a_game_type(%s, %d)", gamename, type); */

	if(gamename == NULL)
		return(NULL);

	for(i = 0; q3a_gametype_map[i].mod != NULL; i++)
		if(strcasecmp(q3a_gametype_map[i].mod, gamename) == 0)
			if(type < q3a_gametype_map[i].number)
				return(q3a_gametype_map[i].gametypes[type]);

	/* no name found, just fall back to the number */
	snprintf(buf, sizeof(buf), "%d", type);

	return(buf);
}

/*
 * searches through returned variables for the specified var, returns value
 * if found, otherwise NULL.
 */
char *q3a_get_var(struct q3a *q, const char *str)
{
	int i;

	/* DEBUG("q3a_get_var(%s)", str); */

	for(i = 0; q->var[i] != NULL; i++)
		if(strcasecmp(q->var[i]->name, str) == 0)
			return(q->var[i]->value);

	return(NULL);
}

/* remove any q3a color escape sequences */
char *q3a_clean_name(const char *name)
{
	int i, str_len = 0;
	char str[Q3A_MAX_NAME_LEN];

	if(name == NULL || name[0] == '\0')
		return(NULL);

	/* DEBUG("q3a_clean_name('%s')", name); */

	/* ^[*] - ^fSome Player ^4Name */
	for(i = 0; name[i] != '\0'; i++) {
		if(name[i] == '^' && name[i + 1] != '\0')
			i++;
		else
			str[str_len++] = name[i];
	}

	str[str_len] = '\0';

#ifdef _DEBUG
	if(strcmp(name, str))
		DEBUG("q3a_clean_name('%s'): '%s'", name, str);
#endif

	return(g_strdup(str));
}

void q3a_usage(void)
{
	printf("%s v%s (%s)\n\n", PROGRAM, VERSION, URL);

	printf("Usage: %s [options] host[:port] [host2:[port]] ...\n", prog);
	printf("  options:\n");
	printf("   -c             compact view (no player list)\n");
	printf("   -g [variable]  show server variable (sets compact)\n");
	printf("   -s             show all server variables (sets compact)\n");
	printf("   -t [timeout]   timeout connecting to server (%d seconds)\n",
		TIMEOUT);
}

/* function to check if a string is a number */
int q3a_isdigit(char *str)
{
	int i;

	DEBUG("q3a_isdigit()");

	/* check each item in the string to make sure it's a number */
	for(i = 0; str[i] != '\0'; i++) {
		if(!isdigit((int) str[i])) {
			int x;

			fprintf(stderr, "%s: %s is not numeric\n", prog, str);

			fprintf(stderr, "%s: ", prog);

			for(x = 0; x < i; x++)
				putc('-', stderr);

			fprintf(stderr, "^\n");

			return(0);
		}
	}

	return(1);
}

/* check if fd is open */
int q3a_is_fd(int fd)
{
	struct stat statbuf;

	return((fstat(fd, &statbuf) == 0));
}

void q3a_free(struct q3a *q)
{
	int i;

	if(q == NULL)
		return;

	DEBUG("q3a_free()");

	if(q->var != NULL) {
		DEBUG("q3a_free(): q->var");

		for(i = 0; q->var[i] != NULL; i++) {
			g_free(q->var[i]->name);
			g_free(q->var[i]->value);

			g_free(q->var[i]);
		}

		g_free(q->var);
	}

	if(q->player != NULL) {
		DEBUG("q3a_free(): q->player");

		for(i = 0; q->player[i] != NULL; i++) {
			g_free(q->player[i]->name);

			g_free(q->player[i]);
		}

		g_free(q->player);
	}

	DEBUG("q3a_free(): q");

	g_free(q);
}

void q3a_show_var(const char *name, const char *value)
{
	if(name == NULL || name[0] == '\0' || value == NULL || value[0] == '\0')
		return;

	printf("    %s = %s\n", name, value);
}

void q3a_debug(const char *fmt, ...)
{
#ifdef _DEBUG
	char buf[2048];

	va_list args;

	va_start(args, fmt);

	vsnprintf(buf, sizeof(buf), fmt, args);

	va_end(args);

	fprintf(stderr, "%s: %s\n", prog, buf);
#else
	return;
#endif
}

char *g_strdup(const char *str)
{
	size_t length;
	char *new_str;

	if(str == NULL)
		return(NULL);

	length = strlen(str) + 1;
	new_str = g_malloc(length);
	memcpy(new_str, str, length);

	return(new_str);
}

void g_free(void *mem)
{
	if(mem)
		free(mem);
}

void *g_malloc(unsigned long n_bytes)
{
	if(n_bytes) {
		void *mem;

		if((mem = malloc(n_bytes)))
			return(mem);

		g_error("g_malloc: unable to allocate %lu bytes", n_bytes);
	}

	return(NULL);
}

void *g_realloc(void *mem, unsigned long n_bytes)
{
	if(n_bytes) {
		if((mem = realloc(mem, n_bytes)))
			return(mem);

		g_error("g_realloc: unable to allocate %lu bytes", n_bytes);
	}

	g_free(mem);

	return(NULL);
}

void g_error(const char *fmt, ...)
{
	char message[255];

	va_list args;

	va_start(args, fmt);

	vsnprintf(message, sizeof(message), fmt, args);

	va_end(args);

	fprintf(stderr, "%s: ** ERROR **: %s\n", prog, message);

	exit(1);
}

/*
 * g_strsplit:
 * @string: a string to split.
 * @delimiter: a string which specifies the places at which to split the string.
 *     The delimiter is not included in any of the resulting strings, unless
 *     @max_tokens is reached.
 * @max_tokens: the maximum number of pieces to split @string into. If this is
 *              less than 1, the string is split completely.
 * 
 * Splits a string into a maximum of @max_tokens pieces, using the given
 * @delimiter. If @max_tokens is reached, the remainder of @string is appended
 * to the last token. 
 *
 * As a special case, the result of splitting the empty string "" is an empty
 * vector, not a vector containing a single string. The reason for this
 * special case is that being able to represent a empty vector is typically
 * more useful than consistent handling of empty elements. If you do need
 * to represent empty elements, you'll need to check for the empty string
 * before calling g_strsplit().
 * 
 * Return value: a newly-allocated %NULL-terminated array of strings. Use 
 *    g_strfreev() to free it.
 *
 * examples:
 *   g_strsplit("one:two:three:four", ":", 1):
 *     array[0] = 'one:two:three:four'
 *
 *   g_strsplit("one:two:three:four", ":", 2):
 *     array[0] = 'one'
 *     array[1] = 'two:three:four'
 *
 *   g_strsplit("one:two:three:four", ":", 0):
 *     array[0] = 'one'
 *     array[1] = 'two'
 *     array[2] = 'three'
 *     array[3] = 'four'
 */

char **g_strsplit(const char *string, const char *delimiter, int max_tokens)
{
	char **str_array, *s;
	unsigned int n = 0, str_array_size = sizeof(char *) + 1;
	const char *remainder;

	if(string == NULL || delimiter == NULL || delimiter[0] == '\0')
		return(NULL);

	if(max_tokens < 1)
		max_tokens = MAXINT;

	remainder = string;

	str_array = g_malloc(str_array_size);

	if((s = strstr(remainder, delimiter))) {
		size_t delimiter_len = strlen(delimiter);

		while(--max_tokens && s) {
			size_t len;
			char *new_string;

			len = s - remainder;

			new_string = g_malloc(len + 1);

			strncpy(new_string, remainder, len);
			new_string[len] = '\0';

			str_array_size += sizeof(char *);

			str_array = g_realloc(str_array, str_array_size);

			str_array[n++] = new_string;

			remainder = s + delimiter_len;

			s = strstr(remainder, delimiter);
		}
	}

	if(*string)
		str_array[n++] = g_strdup(remainder);

	str_array[n] = NULL;

	return(str_array);
}

void g_strfreev(char **str_array)
{
	int i;

	if(str_array == NULL)
		return;

	for(i = 0; str_array[i] != NULL; i++)
		g_free(str_array[i]);

	g_free(str_array);
}

/*
 * --- Changelog --------------------------------------------------------------
 *
 *  0.1 - 2002/03/??:
 *    initial release
 *
 *  0.2 - 2002/03/30:
 *    minor fixes
 *
 *  0.3 - 2002/09/03:
 *    command line args, multiple hosts, output format changes
 *
 *  0.4 - 2002/09/03:
 *    removed -p, port should be specified as host:port, updated alarm handler,
 *      uglified program.
 *
 *  0.5 - 2002/09/18:
 *    better memory managment and handling output from server.
 *
 *  0.6 - 2002/09/19:
 *    additional cleanups.
 *
 *  0.7 - 2002/09/19:
 *    fixed bug with nothing displayed for empty servers, and off by one for
 *      player listing.
 *
 *  0.8 - 2002/10/09:
 *    added -s (show all variables) and -g [var] (show specified variable).
 *
 *  0.9 - 2002/10/11:
 *    fixed a segfault if a server didn't have punkbuster, other minor updates.
 *
 *  1.0 - 2002/10/21:
 *    portability fixes (solaris).
 *
 *  1.1 - 2002/10/28:
 *    improved error handling, other minor updates.
 *
 *  1.2 - 2002/11/06:
 *    added color to cur/max players in status. yellow = server full
 *      (excluding private), red = sever full. compile with -D_NO_COLOR to
 *      disable use of color.
 *
 *  1.3 - 2002/11/07:
 *    fixed a segfault for servers with a large amount of server variables.
 *
 *  1.4 - 2002/11/10:
 *    added check for g_modversion (Q3UT2-2.6). this will display the
 *      [game type]-[version] in the server status.
 *
 *  1.5 - 2003/06/13:
 *    update url, program usage.
 *
 *  1.6 - 2003/08/13:
 *    added proper game type (CTF, FTL, FFA, etc.) handling for q3a, urban
 *      terror (2, 3), ns-co and truecombat (1), taken from xqf.
 *    many other cleanups.
 *
 *  1.7 - 2003/09/07:
 *    removed bsd_strlcpy/cat() and size limitations for players/variables.
 *    don't exit if gethostbyname() fails, just skip that host.
 *    updated strsplit and added other glib-like functions.
 *    added additional game types.
 *    used memprof to take care of some leaks.
 *    removed use of colors (was used only for player totals).
 *    make q3a_clean_name() remove ^* characters, not just ^[0-9].
 *    other cleanups.
 *
 * --- Changelog --------------------------------------------------------------
 */
