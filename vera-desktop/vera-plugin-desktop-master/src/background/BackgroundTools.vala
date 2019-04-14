/*
 * vera-plugin-desktop - desktop plugin for vera
 * Copyright (C) 2014  Eugenio "g7" Paolantonio and the Semplice Project
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

using Vera;

namespace DesktopPlugin {

	public struct BackgroundInfo {
		int x;
		int y;
		int src_w;
		int src_h;
		int dest_w;
		int dest_h;
	}	

	public class BackgroundTools : Object {
		/**
		 * Ever wanted to crop a wallpaper?
		*/
		
		public static BackgroundInfo? get_background_info(BackgroundMode mode, Gdk.Rectangle geometry, Gdk.Pixbuf? pixbuf) {
			/**
			 * Returns an appropriate BackgroundInfo object with the
			 * right values for the given wallpaper.
			*/
			
			if (mode == BackgroundMode.COLOR)
				return null;
			
			BackgroundInfo infos = BackgroundInfo();

			infos.dest_w = geometry.width;
			infos.dest_h = geometry.height;
			infos.src_w = (pixbuf != null) ? pixbuf.get_width() : 0;
			infos.src_h = (pixbuf != null) ? pixbuf.get_height() : 0;
			
			if (mode == BackgroundMode.SCREEN) {
				infos.x = -geometry.x;
				infos.y = -geometry.y;
			} else if (mode == BackgroundMode.CENTER) {
				infos.x = (infos.dest_w - infos.src_w) / 2;
				infos.y = (infos.dest_h - infos.src_h) / 2;
			} else {
				infos.x = 0;
				infos.y = 0;
			}
			
			return infos;
			
		}
			
		
		public static void color(Cairo.Context cx, Gdk.RGBA color) {
			/**
			 * Fills with the given color the supplied Cairo.Context.
			*/
			
			cx.set_source_rgb(
				color.red,
				color.green,
				color.blue
			);
			cx.paint();
			
		}
		
		public static void tile(BackgroundInfo infos, Cairo.Context cx, Gdk.Pixbuf pixbuf) {
			/**
			 * Tiles the given pixbuf in the context.
			*/
			
			/*
			 * Cairo Patterns have a neat way to do tiling,
			 * but we need to have the surface image-sized,
			 * which will be then a no-go when we'll put the thing
			 * as the _XROOTPMAP_ID.
			 * 
			 * So we do tiling the hard way.
			 * There aren't problems when painting outside the bounds
			 * of our subsurface as cairo will not make changes there.
			*/
			
			int tile_w = 0, tile_h;
			
			while (tile_w < infos.dest_w) {
				
				tile_h = 0;
				
				while (tile_h < infos.dest_h) {
					Gdk.cairo_set_source_pixbuf(cx, pixbuf, tile_w, tile_h);
					cx.paint();
					
					tile_h += infos.src_h;
				}
				
				tile_w += infos.src_w;
				
			}
			
		}
		
		public static void stretch(BackgroundInfo infos, Cairo.Context cx, Gdk.Pixbuf pixbuf) {
			/**
			 * Stretches the given pixbuf in the context
			*/
			
			general(
				infos,
				cx,
				(
					(!(infos.dest_w == infos.src_w && infos.dest_h == infos.src_h)) ?
					pixbuf.scale_simple(infos.dest_w, infos.dest_h, Gdk.InterpType.BILINEAR) :
					pixbuf
				)
			);
				
			
		}
		
		public static void crop(BackgroundInfo infos, Cairo.Context cx, Gdk.Pixbuf pixbuf, bool invert_ratio = false) {
			/**
			 * Crops the given pixbuf and then paints it.
			 * 
			 * If invert_ratio = true, the image will instead fit on the
			 * screen.
			*/
			
			int x = infos.x;
			int y = infos.y;
			int new_w = infos.src_w;
			int new_h = infos.src_h;
			bool should_resize = false;
			
			if (infos.dest_w != infos.src_w || infos.dest_h != infos.src_h) {
				
				double w_ratio = (float)infos.dest_w / infos.src_w;
				double h_ratio = (float)infos.dest_h / infos.src_h;
				double ratio = invert_ratio ? double.min(w_ratio, h_ratio) : double.max(w_ratio, h_ratio);
				
				if (ratio != 1.0) {
					
					should_resize = true;
					new_w = ((int)Math.lround(infos.src_w * ratio));
					new_h = ((int)Math.lround(infos.src_h * ratio));
					
				}
				
				x = (infos.dest_w - new_w) / 2;
				y = (infos.dest_h - new_h) / 2;
				
			}
			
			Gdk.cairo_set_source_pixbuf(
				cx,
				(
					should_resize ?
					pixbuf.scale_simple(new_w, new_h, Gdk.InterpType.BILINEAR) :
					pixbuf
				),
				x,
				y
			);
			cx.paint();
			
		}
		
		public static void fit(BackgroundInfo infos, Cairo.Context cx, Gdk.Pixbuf pixbuf) {
			/**
			 * Makes the image fit on the screen, and then paints it.
			 * 
			 * This is equivalent to call crop() with invert_ratio = true.
			*/
			
			crop(
				infos,
				cx,
				pixbuf,
				true
			);
			
		}
		
		public static void general(BackgroundInfo infos, Cairo.Context cx, Gdk.Pixbuf pixbuf) {
			/**
			 * Paints the given pixbuf in the context, without modifying
			 * the image.
			 * 
			 * You can use this for the BackgroundMode.CENTER and
			 * BackgroundMode.SCREEN images, as the only change are the 
			 * coordinates in the BackgroundInfo struct and they are
			 * determined automatically anyway by get_background_info().
			*/
			
			Gdk.cairo_set_source_pixbuf(
				cx,
				pixbuf,
				infos.x,
				infos.y
			);
			cx.paint();
			
		}

	}
	
}
