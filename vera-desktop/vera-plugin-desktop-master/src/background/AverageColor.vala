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

/* TODO: LUMA
 * int64 luma = Math.lround(0.2126 * red + 0.7152 * green + 0.0722 * blue);
*/

namespace DesktopPlugin {

	public class AverageColor : Object {
        
		/* The following color averaging algorithm was originally written for
		   Unity in C++, then patched into gnome-desktop3 in C.  It has
		   then been ported to Vala for unity-greeter.
		   Source of the file: http://bazaar.launchpad.net/~unity-greeter-team/unity-greeter/trunk/view/head:/src/background.vala
		   
		   Authors of the code:
		   Robert Ancell <robert.ancell@canonical.com>
		   Michael Terry <michael.terry@canonical.com>
		*/

		static const int QUAD_MAX_LEVEL_OF_RECURSION = 16;
		static const int QUAD_MIN_LEVEL_OF_RECURSION = 2;
		static const int QUAD_CORNER_WEIGHT_NW       = 3;
		static const int QUAD_CORNER_WEIGHT_NE       = 1;
		static const int QUAD_CORNER_WEIGHT_SE       = 1;
		static const int QUAD_CORNER_WEIGHT_SW       = 3;
		static const int QUAD_CORNER_WEIGHT_CENTER   = 2;
		static const int QUAD_CORNER_WEIGHT_TOTAL    = (QUAD_CORNER_WEIGHT_NW + QUAD_CORNER_WEIGHT_NE + QUAD_CORNER_WEIGHT_SE + QUAD_CORNER_WEIGHT_SW + QUAD_CORNER_WEIGHT_CENTER);

		/* Pixbuf utilities */
		private static Gdk.RGBA get_pixbuf_sample (uint8[]   pixels,
											int       rowstride,
											int       channels,
											int       x,
											int       y)
		{
			var sample = Gdk.RGBA ();
			double dd = 0xFF;
			int offset = ((y * rowstride) + (x * channels));

			sample.red = pixels[offset++] / dd;
			sample.green = pixels[offset++] / dd;
			sample.blue = pixels[offset++] / dd;
			sample.alpha = 1.0f;

			return sample;
		}

		private static bool is_color_different (Gdk.RGBA color_a,
										 Gdk.RGBA color_b)
		{
			var diff = Gdk.RGBA ();

			diff.red   = color_a.red   - color_b.red;
			diff.green = color_a.green - color_b.green;
			diff.blue  = color_a.blue  - color_b.blue;
			diff.alpha = 1.0f;

			if (GLib.Math.fabs (diff.red) > 0.15 ||
				GLib.Math.fabs (diff.green) > 0.15 ||
				GLib.Math.fabs (diff.blue) > 0.15)
				return true;

			return false;
		}

		private static Gdk.RGBA get_quad_average (int       x,
										   int       y,
										   int       width,
										   int       height,
										   int       level_of_recursion,
										   uint8[]   pixels,
										   int       rowstride,
										   int       channels)
		{
			// samples four corners
			// c1-----c2
			// |       |
			// c3-----c4

			var average = Gdk.RGBA ();
			var corner1 = get_pixbuf_sample (pixels, rowstride, channels, x        , y         );
			var corner2 = get_pixbuf_sample (pixels, rowstride, channels, x + width, y         );
			var corner3 = get_pixbuf_sample (pixels, rowstride, channels, x        , y + height);
			var corner4 = get_pixbuf_sample (pixels, rowstride, channels, x + width, y + height);
			var centre  = get_pixbuf_sample (pixels, rowstride, channels, x + (width / 2), y + (height / 2));

			/* If we're over the max we want to just take the average and be happy
			   with that value */
			if (level_of_recursion < QUAD_MAX_LEVEL_OF_RECURSION) {
				/* Otherwise we want to look at each value and check it's distance
				   from the center color and take the average if they're far apart. */

				/* corner 1 */
				if (level_of_recursion < QUAD_MIN_LEVEL_OF_RECURSION ||
						is_color_different(corner1, centre)) {
					corner1 = get_quad_average (x, y, width/2, height/2, level_of_recursion + 1, pixels, rowstride, channels);
				}

				/* corner 2 */
				if (level_of_recursion < QUAD_MIN_LEVEL_OF_RECURSION ||
						is_color_different(corner2, centre)) {
					corner2 = get_quad_average (x + width/2, y, width/2, height/2, level_of_recursion + 1, pixels, rowstride, channels);
				}

				/* corner 3 */
				if (level_of_recursion < QUAD_MIN_LEVEL_OF_RECURSION ||
						is_color_different(corner3, centre)) {
					corner3 = get_quad_average (x, y + height/2, width/2, height/2, level_of_recursion + 1, pixels, rowstride, channels);
				}

				/* corner 4 */
				if (level_of_recursion < QUAD_MIN_LEVEL_OF_RECURSION ||
						is_color_different(corner4, centre)) {
					corner4 = get_quad_average (x + width/2, y + height/2, width/2, height/2, level_of_recursion + 1, pixels, rowstride, channels);
				}
			}

			average.red   = ((corner1.red * QUAD_CORNER_WEIGHT_NW)     +
							 (corner3.red * QUAD_CORNER_WEIGHT_SW)     +
							 (centre.red  * QUAD_CORNER_WEIGHT_CENTER) +
							 (corner2.red * QUAD_CORNER_WEIGHT_NE)     +
							 (corner4.red * QUAD_CORNER_WEIGHT_SE))
							/ QUAD_CORNER_WEIGHT_TOTAL;
			average.green = ((corner1.green * QUAD_CORNER_WEIGHT_NW)     +
							 (corner3.green * QUAD_CORNER_WEIGHT_SW)     +
							 (centre.green  * QUAD_CORNER_WEIGHT_CENTER) +
							 (corner2.green * QUAD_CORNER_WEIGHT_NE)     +
							 (corner4.green * QUAD_CORNER_WEIGHT_SE))
							/ QUAD_CORNER_WEIGHT_TOTAL;
			average.blue  = ((corner1.blue * QUAD_CORNER_WEIGHT_NW)     +
							 (corner3.blue * QUAD_CORNER_WEIGHT_SW)     +
							 (centre.blue  * QUAD_CORNER_WEIGHT_CENTER) +
							 (corner2.blue * QUAD_CORNER_WEIGHT_NE)     +
							 (corner4.blue * QUAD_CORNER_WEIGHT_SE))
							/ QUAD_CORNER_WEIGHT_TOTAL;
			average.alpha = 1.0f;

			return average;
		}

		public static Gdk.RGBA pixbuf_average_RGBA (Gdk.Pixbuf pixbuf)
		{
			var average = get_quad_average (0, 0,
											pixbuf.get_width () - 1, pixbuf.get_height () - 1,
											1,
											pixbuf.get_pixels (),
											pixbuf.get_rowstride (),
											pixbuf.get_n_channels ());

			return average;
		}
		
		public static string pixbuf_average_value (Gdk.Pixbuf pixbuf)
		{
			return pixbuf_average_RGBA(pixbuf).to_string();
		}
		
	}

}
