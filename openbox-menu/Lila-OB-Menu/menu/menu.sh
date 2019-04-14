#!/bin/bash
# File Name:menu.sh
# Version: 1.0.12
# Authors: by ilnanny
# Acknowledgements: Original script by KDulcimer of TinyMe. http://tinyme.mypclinuxos.com
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
###################################################################################################################################

TEXTDOMAINDIR=/usr/share/locale
TEXTDOMAIN=menu.sh
ED1=leafpad
TERM=xfce4-terminal

 
export ControlCenter=$(cat <<End_of_Text
<window title="Lila Control Center" window-position="1"  icon-name="preferences-desktop" decorated="true" allow-grow="false">
<vbox>
 
          
     
                 <pixmap><height>48</height><width>48</width>
                 <input file>/usr/share/pixmaps/menu.png</input>
                 </pixmap>
                 <text use-markup="true" width-chars="50">
                 <label>"<b>`gettext $"Lila Debian Menu"`</b>"</label>
                 </text>
               
 
        <hbox>
          <button tooltip-text="`gettext $"About"`" height-request="28" width-request="28">
          <input file stock="gtk-dialog-info"></input>
          <action>/usr/local/bin/menu/license</action>
          </button>
         </hbox>

          
<notebook tab-pos="0" labels="Appearance|System|Openbox|Session|Personal|Hardware">
      
	<hbox homogeneous="true">
	  <vbox>
		<hbox> 
		  <button tooltip-text="`gettext $"Choose Wallpaper"`" height-request="60" width-request="60"  stock-icon-size="6" relief="2">
          <input file icon="wallpaper"></input><height>48</height><width>48</width>
          <action>nitrogen &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Wallpaper"`"</label>
		  </text>
		</hbox>
<hbox>
<button tooltip-text="`gettext $"Yanima wallpaper changer setup"`" height-request="60" width-request="60"  stock-icon-size="6" relief="2">
          <input file icon="wallpaper"></input><height>48</height><width>48</width>
          <action>/usr/local/bin/yanima/settings.sh</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Yanima settings"`"</label>
		  </text>
</hbox>
          </vbox>
          <vbox> 
		<hbox>
          <button tooltip-text="`gettext $"Change Gtk2 and Icon Themes"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" >
          <input file icon="style"></input><height>48</height><width>48</width>
		  <action>/usr/local/bin/styler/styler.sh &</action>
          </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Appearance"`"</label>
		  </text>
		</hbox>
<hbox>
<button tooltip-text="`gettext $"Screensaver"`" height-request="60" width-request="60"  stock-icon-size="6" relief="2">
          <input file icon="xscreensaver"></input><height>48</height><width>48</width>
          <action>xscreensaver-demo</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Screensaver"`"</label>
		  </text>
</hbox>
        
	  </vbox>
<vbox> 
        <hbox>
		  <button tooltip-text="`gettext $"Openbox Config"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="preferences-system"></input><height>48</height><width>48</width>
		  <action> /usr/bin/obconf &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Obconf"`"</label>
		  </text>
		</hbox>
        
	  </vbox>
	</hbox>
       <hbox homogeneous="true">
	  <vbox>
        <hbox>
		  <button tooltip-text="`gettext $"Configure System"`" height-request="60" width-request="60" stock-icon-size="6" relief="2">
		  <input file icon="preferences-system"></input><height>48</height><width>48</width>
		  <action>gksudo $ED1 /etc/fstab /etc/default/keyboard /etc/default/grub /etc/apt/sources.list &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"System"`"</label>
		  </text>
		</hbox>
		        
        	
       </vbox>
       <vbox>         
                <hbox>
                  <button tooltip-text="`gettext $"Synaptic Package Manager"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
                  <input file icon="synaptic"></input><height>48</height><width>48</width>
                  <action>gksudo synaptic</action>
                  </button>
                  <text use-markup="true" width-chars="12">
                  <label>"`gettext $"Synaptic Package Manager"`"</label>
                  </text>
                </hbox> 

           </vbox>

	</hbox>
       <hbox  homogeneous="true">
	  <vbox>
	    <hbox>
         <button tooltip-text="`gettext $"Edit rc file"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" >
		  <input file icon="accessories-text-editor"></input><height>48</height><width>48</width>
		  <action>$ED1 ~/.config/openbox/rc.xml &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Edit rc"`"</label>
		  </text>
		</hbox>
		<hbox>
		  <button tooltip-text="`gettext $"Choose Startup Services"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="gnome-settings"></input><height>48</height><width>48</width>
		  <action>$ED1 ~/.config/openbox/autostart.sh</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Startup Services"`"</label>
		  </text>
		</hbox>
             </vbox>
	  <vbox>
		<hbox>
		  <button tooltip-text="`gettext $"Set Keyboard shortcuts"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="input-keyboard"></input><height>48</height><width>48</width>
		  <action>obkey &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Obkey"`"</label>
		  </text>
		</hbox>
                <hbox>
		  <button tooltip-text="`gettext $"Edit menu"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="applications-system"></input><height>48</height><width>48</width>
		  <action>obmenu  &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Menu"`"</label>
		  </text>
		</hbox> 
	  </vbox>
	</hbox>
	 <hbox  homogeneous="true"> 
              <vbox>
                <hbox>
		  <button tooltip-text="`gettext $"Edit Login Options"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="lightdm-gtk-greeter-settings"></input><height>48</height><width>48</width>
		  <action>gksudo $ED1 /etc/lightdm/lightdm-gtk-greeter.conf</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Login Options"`"</label>
		  </text>
 		</hbox>
                <hbox>
		  <button tooltip-text="`gettext $"LightDM Gtk+ greeter settings"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="lightdm-gtk-greeter-settings"></input><height>48</height><width>48</width>
		  <action>gksudo /usr/bin/lightdm-gtk-greeter-settings-pkexec &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"LightDM"`"</label>
		  </text>
                </hbox>
            </vbox>
	       <vbox>
                <hbox>
		  <button tooltip-text="`gettext $"Set auto-login"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="user-info"></input><height>48</height><width>48</width>
		  <action>gksudo $ED1 /etc/lightdm/lightdm.conf &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Auto-login"`"</label>
		  </text>
		</hbox>
        <hbox>
		  <button tooltip-text="`gettext $"Users and Groups Settings"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="system-users"></input><height>48</height><width>48</width>
		  <action>users-admin</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Users and Groups"`"</label>
		  </text>
		</hbox>
	  </vbox>
	</hbox>
      <hbox  homogeneous="true">
         <vbox>
      <hbox>
		  <button tooltip-text="`gettext $"Preferred Applications"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" >
		  <input file icon="preferences-desktop-default-applications"></input><height>48</height><width>48</width>
		  <action>exo-preferred-applications</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Preferred Applications"`"</label>
		  </text>
		</hbox> 
       </vbox>
	  <vbox>
       <hbox>
           <button tooltip-text="`gettext $"Qt 4 Settings"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" >
		  <input file icon="qtconfig-qt4"></input><height>48</height><width>48</width>
		  <action>qtconfig-qt4</action>
           </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Qt 4"`"</label>
		  </text>
		</hbox>
            </vbox>
	</hbox>
       <hbox  homogeneous="true">
	  <vbox>
               <hbox>
		  <button tooltip-text="`gettext $"Configure Mouse and Touchpad"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="input-mouse"></input><height>48</height><width>48</width>
		  <action>gpointing-device-settings &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Mouse and Touchpad"`"</label>
		  </text>
		</hbox>
             
                <hbox>
		  <button tooltip-text="`gettext $"Set Screen Resolution"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="display"></input><height>48</height><width>48</width>
		  <action>arandr</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Screen"`"</label>
		  </text>
		</hbox>
        <hbox>
		  <button tooltip-text="`gettext $"Printer"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="printer"></input><height>48</height><width>48</width>
		  <action>system-config-printer</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Printer"`"</label>
		  </text>
		</hbox>
</vbox>

          <vbox>
		<hbox>
		  <button tooltip-text="`gettext $"Change Keyboard Layout"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="input-keyboard"></input><height>48</height><width>48</width>
		  <action>lxkeymap &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Keyboard Layout"`"</label>
		  </text>
		</hbox>
		<hbox>
		  <button tooltip-text="`gettext $"Power Management"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="ac-adapter"></input><height>48</height><width>48</width>
		  <action>xfce4-power-manager-settings</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Power Management"`"</label>
		  </text>
        </hbox>
<hbox>
		  <button tooltip-text="`gettext $"Adjust Mixer"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="multimedia-volume-control"></input><height>48</height><width>48</width>
		  <action>pavucontrol &</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Mixer"`"</label>
		  </text>
		</hbox> 

        
 </vbox>
<vbox>
          <hbox>
                  <button tooltip-text="`gettext $"PC Information"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
                  <input file icon="utilities-system-monitor"></input><height>48</height><width>48</width>
                  <action>/usr/local/bin/menu/inxi-gui &</action>
                  </button>
                  <text use-markup="true" width-chars="12">
                  <label>"`gettext $"PC Information"`"</label>
                  </text>
                </hbox>
<hbox>
		  <button tooltip-text="`gettext $"Net tools"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="gnome-nettool"></input><height>48</height><width>48</width>
		  <action>gnome-nettool</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Net"`"</label>
		  </text>
		</hbox>
 
<hbox>
		  <button tooltip-text="`gettext $"Execute Test Sound"`" height-request="60" width-request="60" stock-icon-size="6" relief="2" > 
		  <input file icon="multimedia-volume-control"></input><height>48</height><width>48</width>
		  <action>/usr/local/bin/menu/test_sound</action>
		  </button>
		  <text use-markup="true" width-chars="12">
		  <label>"`gettext $"Test Sound"`"</label>
		  </text>
		</hbox> 

	  </vbox>
	</hbox>
    
 </notebook> 

<hbox>
<vbox>
    <hbox>
        <button>
          <input file stock="gtk-close"></input>
          <label>"`gettext $"Close"`"</label>
          <action>EXIT:cancel</action>
         </button>
     </hbox>
</vbox>
</hbox>

</vbox>
</window>
End_of_Text
)
gtkdialog --program=ControlCenter
unset ControlCenter
