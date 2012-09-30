/*
 * game.hpp
 * 
 * Copyright 2012 Robert Knauer <robert@privatdemail.net>
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 * 
 * 
 */
#ifndef GAME_HPP
#	define GAME_HPP
	
#	include <iostream>
#	include <SFML/Window.hpp>
#	include <libintl.h>
#	include "padding_data_calculator.hpp"
#	include "cursor.hpp"
#	include "config.hpp"
#	include "fps_counter.hpp"
#	include "gamemodes/main_menu.hpp"
#	include "gamemodes/settings_menu.hpp"
#	include "gamemodes/settings_general_menu.hpp"
#	include "gamemodes/settings_graphics_menu.hpp"
#	include "gamemodes/settings_control_menu.hpp"
#	include "gamemodes/settings_sound_menu.hpp"
#	include "event_processor_return.hpp"
#	include "universal_drawable.hpp"
	
	class Game
	{
		public:
			Game();
			virtual ~Game();
			
			/*
			 * (Un)Init game:
			*/
			int init(void);
			int uninit(void);
			/*
			 * Start main loop:
			*/
			int loop(void);
		private:
			/*
			 * Init locale:
			*/
			int init_locale(void);
			/*
			 * Set language:
			*/
			int set_language(std::string lang);
			/*
			 * Wait for focus:
			*/
			int wait_for_focus(void);
			/*
			 * Process events:
			*/
			int process_events(void);
			/*
			 * Calculate sizes:
			*/
			int calculate_sizes(void);
			/*
			 * Set game mode:
			*/
			int set_gamemode(int gamemode);
			/*
			 * (Un)init game mode:
			*/
			int init_gamemode(int gamemode);
			int uninit_gamemode(int gamemode);
			
			/*
			 * Internal variables:
			*/
			int m_screen_w;
			int m_screen_h;
			int m_screen_bits;
			int m_framerate_frames;
			int m_window_has_focus;
			sf::RenderWindow m_window;
			sf::RenderTexture m_texture;
			PaddingDataCalculator m_padding_data_calculator;
			Cursor m_cursor;
			Config m_config;
			FPScounter m_fps_counter;
			MainMenu *m_main_menu;
			SettingsMenu *m_settings_menu;
			SettingsGeneralMenu *m_settings_general_menu;
			SettingsGraphicsMenu *m_settings_graphics_menu;
			SettingsControlMenu *m_settings_control_menu;
			SettingsSoundMenu *m_settings_sound_menu;
			/*
			 * Game mode:
			 *  0 - undefined
			 *  1 - main menu
			 *  2 - settings menu
			 *  3 - settings general menu
			 *  4 - settings graphics menu
			 *  5 - settings control menu
			 *  6 - settings sound menu
			*/
			int m_gamemode;
	};
#endif // GAME_HPP
