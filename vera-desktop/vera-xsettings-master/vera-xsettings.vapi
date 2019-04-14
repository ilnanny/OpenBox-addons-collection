/*
 * vera-xsettings.vapi - vala bindings for libvera-xsettings
 * Copyright (C) 2014  Eugenio "g7" Paolantonio and the Semplice Project
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Authors:
 *     Eugenio "g7" Paolantonio <me@medesimo.eu>
*/

[CCode (cprefix = "", lower_case_cprefix = "", cheader_filename = "vera-xsettings/xsettings-manager.h,vera-xsettings/xsettings-common.h")]
namespace XSettings {

	[CCode (cname = "XSettingsTerminateFunc", has_type_id = false)]
	public delegate void TerminateFunc ();
	
	/*
	 * FIXME: unforunately it seems that vala destroys the Manager
	 * ASAP when specifying the free_function.
	 * 
	 * We do not want that. This needs to be fixed, as automatic freeing
	 * of object is good and great.
	 * For now please destroy the manager with the built in destroy()
	 * method.
	*/
	//[CCode (cname = "XSettingsManager", free_function = "xsettings_manager_destroy")]
	[CCode (cname = "XSettingsManager", free_function = "")]
	[Compact]
	public class Manager {
		[CCode (cname = "xsettings_manager_check_running")]
		public static bool check_running (X.Display display, int screen);
		
		[CCode (cname = "xsettings_manager_new")]
		public Manager (X.Display display, int screen, TerminateFunc terminate);
		
		[CCode (cname = "xsettings_manager_destroy")]
		public void destroy ();
		
		[CCode (cname = "xsettings_manager_get_window")]
		public X.Window get_window ();
		
		[CCode (cname = "xsettings_manager_process_event")]
		public bool process_event (X.Event xev);
		
		[CCode (cname = "xsettings_manager_set_setting")]
		public Result set_setting (Setting setting);
		
		[CCode (cname = "xsettings_manager_delete_setting")]
		public Result delete_setting (string name);
		
		[CCode (cname = "xsettings_manager_set_int")]
		public Result set_int (string name, int value);
		
		[CCode (cname = "xsettings_manager_set_string")]
		public Result set_string (string name, string value);
		
		[CCode (cname = "xsettings_manager_set_color")]
		public Result set_color (string name, Color value);
		
		[CCode (cname = "xsettings_manager_notify")]
		public Result notify ();

	}

	[CCode (cname = "XSettingsType", cprefix = "XSETTINGS_TYPE_", has_type_id = false)]
	public enum Type {
		INT,
		STRING,
		COLOR;
	}

	[CCode (cname = "XSettingsResult", cprefix = "XSETTINGS_", has_type_id = false)]
	public enum Result {
	  SUCCESS,
	  NO_MEM,
	  ACCESS,
	  FAILED,
	  NO_ENTRY,
	  DUPLICATE_ENTRY;
	}

	[CCode (cname = "XSettingsBuffer", destroy_function = "", has_type_id = false)]
	public struct Buffer {
	  public char byte_order;
	  size_t len;
	  uchar *data;
	  uchar *pos;
	}

	[CCode (cname = "XSettingsColor", destroy_function = "", has_type_id = false)]
	public struct Color {
		ushort red;
		ushort green;
		ushort blue;
		ushort alpha;
	}

	/*
	 * FIXME: vala complains here about recursive declaration (that 'next'
	 * List object).
	 * We need to fix that.
	*/
	
	/*
	[CCode (cname = "XSettingsList", destroy_function = "xsettings_list_free", has_type_id = false)]
	public struct List {
	  Setting setting;
	  List next;
	  
	  [CCode (cname = "xsettings_list_copy")]
	  public List copy ();
	  
	  [CCode (cname = "xsettings_list_insert")]
	  public Result insert (Setting setting);
	  
	  [CCode (cname = "xsettings_list_lookup")]
	  public Setting lookup (string name);
	  
	  [CCode (cname = "xsettings_list_delete")]
	  public Result delete (string name);
	}
	*/


	[CCode (cname = "XSettingsSetting", destroy_function = "xsettings_setting_free", has_type_id = false)]
	public struct Setting {
	  string name;
	  Type type;
	  
	  [CCode (cname = "data.v_int")]
	  int data_v_int;
	  
	  [CCode (cname = "data.v_string")]
	  string data_v_string;
	  
	  [CCode (cname = "data.v_color")]
	  Color data_v_color;

	  ulong last_change_serial;
	  
	  [CCode (cname = "xsettings_setting_copy")]
	  public Setting copy ();
	  
	  [CCode (cname = "xsettings_setting_equal")]
	  public int equal (Setting setting_b);
	  
	}

}
