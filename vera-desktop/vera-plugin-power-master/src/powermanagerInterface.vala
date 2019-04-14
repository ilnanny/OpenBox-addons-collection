/*
 * vera-plugin-power - power plugin for vera
 * Copyright (C) 2014-2015  Eugenio "g7" Paolantonio and the Semplice Project
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Authors:
 *     Eugenio "g7" Paolantonio <me@medesimo.eu>
*/


namespace Vera {
	
	[DBus (name = "org.semplicelinux.vera.powermanager")]
	public interface VeraPowerManager : Object {
		/**
		 * The VeraPowerManager DBus interface.
		*/ 
		
		public signal void BrightnessChanged(int level);
		
		public abstract void IncreaseBrightness() throws IOError;
		public abstract void DecreaseBrightness() throws IOError;
		public abstract void SetBrightness(int new_value) throws IOError;
		public abstract int GetBrightness() throws IOError;
		public abstract bool IsBacklightSupported() throws IOError;
	}

}
