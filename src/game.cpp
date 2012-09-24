/*
 * game.cpp
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
#include "game.hpp"

Game::Game()
{
	
}
Game::~Game()
{
	
}
int Game::init(void)
{
	/*
	 * Variable declarations:
	*/
	sf::VideoMode videomode;
	/*
	 * Load configuration:
	*/
	m_config.load();
	m_config.dump();
	if (m_config.write() == 1)
		return 1;
	/*
	 * Get video info:
	*/
	std::cout << "Getting video mode...";
	videomode = sf::VideoMode::getDesktopMode();
	std::cout << "[DONE]" << std::endl;
	std::cout << "  Screen Resolution: " << videomode.width << "x" << videomode.height << "x" << videomode.bitsPerPixel << std::endl;
	m_screen_bits = videomode.bitsPerPixel;
	/*
	 * Check forced screen width:
	*/
	if (m_config.get("GRAPHICS__RESOLUTION_X").value_int == 0)
	{
		m_screen_w = videomode.width;
	}
	else
	{
		m_screen_w = m_config.get("GRAPHICS__RESOLUTION_X").value_int;
		std::cout << "  Forced Screen Width: " << m_screen_w << std::endl;
	};
	/*
	 * Check forced screen height:
	*/
	if (m_config.get("GRAPHICS__RESOLUTION_Y").value_int == 0)
	{
		m_screen_h = videomode.height;
	}
	else
	{
		m_screen_h = m_config.get("GRAPHICS__RESOLUTION_Y").value_int;
		std::cout << "  Forced Screen Height: " << m_screen_h << std::endl;
	};
	/*
	 * Init locale:
	*/
	if (init_locale() == 1)
		return 1;
	/*
	 * Create window:
	*/
	std::cout << "Creating window (" << m_screen_w << "x" << m_screen_h << "x" << m_screen_bits << ")... ";
	if (m_config.get("GRAPHICS__FULLSCREEN").value_bool)
		m_window.create(videomode, "Game", sf::Style::Fullscreen);
	else
		m_window.create(sf::VideoMode(m_screen_w, m_screen_h, m_screen_bits), "Game");
	std::cout << "[DONE]" << std::endl;
	m_window_has_focus = 1;
	/*
	 * Calculate padding data:
	*/
	m_padding_data_calculator.set_screen_w(m_screen_w);
	m_padding_data_calculator.set_screen_h(m_screen_h);
	m_padding_data_calculator.calculate();
	/*
	 * Create padded texture:
	*/
	std::cout << "Creating padded texture... ";
	if (!m_texture.create(m_padding_data_calculator.get_usable_w(), m_padding_data_calculator.get_usable_h()))
	{
		std::cout << "[FAIL]" << std::endl;
		return 1;
	};
	std::cout << "[DONE]" << std::endl;
	/*
	 * Init cursor:
	*/
	m_window.setMouseCursorVisible(false);
	if (m_cursor.init() == 1)
		return 1;
	m_cursor.set_mouse_position(
		sf::Mouse::getPosition().x,
		sf::Mouse::getPosition().y
	);
	/*
	 * Init framecounter:
	*/
	m_fps_counter.init(m_padding_data_calculator.get_usable_h());
	/*
	 * Show main menu:
	*/
	m_gamemode = 0;
	if (set_gamemode(1) == 1)
		return 1;
	/*
	 * Finish successful:
	*/
	return EXIT_SUCCESS;
}
int Game::uninit(void)
{
	uninit_gamemode(m_gamemode);
	m_window.close();
	return EXIT_SUCCESS;
}
int Game::loop(void)
{
	/*
	 * Variable definitons:
	*/
	int done = 0;
	sf::Sprite sprite;
	/*
	 * Main loop:
	*/
	while (done == 0)
	{
		/*
		 * Process events:
		*/
		done = process_events();
		/*
		 * Check if we have to draw the stuff:
		*/
		if (m_window_has_focus == 1)
		{
			/*
			 * Clean window and padded texture:
			*/
			m_window.clear();
			m_texture.clear(sf::Color(170, 217, 152));
			/*
			 * Draw everything on padded texture and show it:
			*/
			switch (m_gamemode)
			{
				case 1:
					/*
					 * Main Menu
					*/
					draw_main_menu();
					break;
				case 2:
					/*
					 * Settings Menu
					*/
					draw_settings_menu();
					break;
				case 3:
					/*
					 * Settings General Menu
					*/
					draw_settings_general_menu();
					break;
				case 4:
					/*
					 * Settings Graphics Menu
					*/
					draw_settings_graphics_menu();
					break;
				case 5:
					/*
					 * Settings Control Menu
					*/
					draw_settings_control_menu();
					break;
				case 6:
					/*
					 * Settings Sound Menu
					*/
					draw_settings_sound_menu();
					break;
			}
			m_texture.draw(m_cursor.get_drawable(
				m_padding_data_calculator.get_usable_w(),
				m_padding_data_calculator.get_usable_h()
			));
			m_texture.draw(m_fps_counter.get_drawable());
			m_texture.display();
			/*
			 * Draw padded texture on window and show it:
			*/
			sprite = sf::Sprite();
			sprite.setTexture(m_texture.getTexture());
			sprite.setPosition(
				m_padding_data_calculator.get_padding_x(),
				m_padding_data_calculator.get_padding_y()
			);
			m_window.draw(sprite);
			m_window.display();
		}
		else
		{
			/*
			 * We have no focus, so we sleep:
			*/
			if (wait_for_focus() == 1)
				return 1;
		};
	}
	return done;
}
int Game::init_locale(void)
{
	setenv("LANGUAGE", m_config.get("GENERAL__LANGUAGE").value_string.c_str(), 1);
	setlocale(LC_ALL, "");
	bindtextdomain("sf-game", "./locale");
	textdomain("sf-game");
	return 0;
}
int Game::wait_for_focus(void)
{
	/*
	 * Variable declarations:
	*/
	sf::Event event;
	/*
	 * Wait for events:
	*/
	while (m_window.waitEvent(event))
	{
		switch (event.type)
		{
			case sf::Event::GainedFocus:
				std::cout << "GainedFocus" << std::endl;
				m_window_has_focus = 1;
				m_fps_counter.restart();
				return 0;
				break;
			case sf::Event::Closed:
				std::cout << "QUIT signal received." << std::endl;
				return 1;
				break;
		}
	}
}
int Game::process_events(void)
{
	/*
	 * Variable definitions:
	*/
	sf::Event event;
	int x, y;
	int res = -2;
	/*
	 * Check for events:
	*/
	while (m_window.pollEvent(event))
	{
		/*
		 * Handle important events:
		*/
		switch (event.type)
		{
			case sf::Event::Closed:
				std::cout << "QUIT signal received." << std::endl;
				return 1;
				break;
			case sf::Event::KeyPressed:
				std::cout << "KeyPressed " << event.key.code << std::endl;
				break;
			case sf::Event::MouseMoved:
				/*
				 * Calculate new mouse position:
				*/
				x = event.mouseMove.x-m_padding_data_calculator.get_padding_x();
				y = event.mouseMove.y-m_padding_data_calculator.get_padding_y();
				if (x < 0)
					x = 0;
				else if (x > m_padding_data_calculator.get_usable_w())
					x = m_padding_data_calculator.get_usable_w();
				if (y < 0)
					y = 0;
				else if (y > m_padding_data_calculator.get_usable_h())
					y = m_padding_data_calculator.get_usable_h();
				/*
				 * Set mouse position:
				*/
				m_cursor.set_mouse_position(x, y);
				break;
			case sf::Event::MouseButtonPressed:
				std::cout << "MouseButtonPressed ";
				switch (event.mouseButton.button)
				{
					case sf::Mouse::Left:
						std::cout << "LEFT";
						m_cursor.activate_action_cursor();
						break;
					case sf::Mouse::Middle:
						std::cout << "MIDDLE";
						break;
					case sf::Mouse::Right:
						std::cout << "RIGHT";
						break;
				}
				x = event.mouseButton.x-m_padding_data_calculator.get_padding_x();
				y = event.mouseButton.y-m_padding_data_calculator.get_padding_y();
				if (x < 0)
					x = 0;
				else if (x > m_padding_data_calculator.get_usable_w())
					x = m_padding_data_calculator.get_usable_w();
				if (y < 0)
					y = 0;
				else if (y > m_padding_data_calculator.get_usable_h())
					y = m_padding_data_calculator.get_usable_h();
				std::cout << " @ (" << x << "," << y << ")" << std::endl;
				break;
			case sf::Event::MouseButtonReleased:
				std::cout << "MouseButtonReleased ";
				switch (event.mouseButton.button)
				{
					case sf::Mouse::Left:
						std::cout << "LEFT";
						m_cursor.deactivate_action_cursor();
						break;
					case sf::Mouse::Middle:
						std::cout << "MIDDLE";
						break;
					case sf::Mouse::Right:
						std::cout << "RIGHT";
						break;
				}
				x = event.mouseButton.x-m_padding_data_calculator.get_padding_x();
				y = event.mouseButton.y-m_padding_data_calculator.get_padding_y();
				if (x < 0)
					x = 0;
				else if (x > m_padding_data_calculator.get_usable_w())
					x = m_padding_data_calculator.get_usable_w();
				if (y < 0)
					y = 0;
				else if (y > m_padding_data_calculator.get_usable_h())
					y = m_padding_data_calculator.get_usable_h();
				std::cout << " @ (" << x << "," << y << ")" << std::endl;
				break;
			case sf::Event::LostFocus:
				std::cout << "LostFocus" << std::endl;
				m_window_has_focus = 0;
				break;
			case sf::Event::GainedFocus:
				std::cout << "GainedFocus" << std::endl;
				m_window_has_focus = 1;
				m_fps_counter.restart();
				break;
		}
		/*
		 * And then let the gamemode classes handle them:
		*/
		switch (m_gamemode)
		{
			case 1:
				/*
				 * Main Menu
				*/
				res = m_main_menu->process_event(
					event,
					m_cursor.get_mouse_position_x(),
					m_cursor.get_mouse_position_y()
				);
				break;
			case 2:
				/*
				 * Settings Menu
				*/
				res = m_settings_menu->process_event(
					event,
					m_cursor.get_mouse_position_x(),
					m_cursor.get_mouse_position_y()
				);
				break;
			case 3:
				/*
				 * Settings General Menu
				*/
				res = m_settings_general_menu->process_event(
					event,
					m_cursor.get_mouse_position_x(),
					m_cursor.get_mouse_position_y()
				);
				break;
			case 4:
				/*
				 * Settings Graphics Menu
				*/
				res = m_settings_graphics_menu->process_event(
					event,
					m_cursor.get_mouse_position_x(),
					m_cursor.get_mouse_position_y()
				);
				break;
			case 5:
				/*
				 * Settings Control Menu
				*/
				res = m_settings_control_menu->process_event(
					event,
					m_cursor.get_mouse_position_x(),
					m_cursor.get_mouse_position_y()
				);
				break;
			case 6:
				/*
				 * Settings Sound Menu
				*/
				res = m_settings_sound_menu->process_event(
					event,
					m_cursor.get_mouse_position_x(),
					m_cursor.get_mouse_position_y()
				);
				break;
		}
		if (res == -1)
			return 1; // exit
		else if (res == 0 || res == -2)
			continue; // go on
		else
			if (set_gamemode(res) == 1) // set gamemode
				return 1; // setting gamemode failed, exit
	}
	/*
	 * Finish successful:
	*/
	return 0;
}
int Game::calculate_sizes(void)
{
	/*
	 * Calculate element sizes for new screen size:
	*/
	switch (m_gamemode)
	{
		case 1:
			/*
			 * Main Menu
			*/
			if (m_main_menu->calculate_sizes(
				m_padding_data_calculator.get_usable_w(),
				m_padding_data_calculator.get_usable_h()
			) == 1)
				return 1;
			return 0;
			break;
		case 2:
			/*
			 * Settings Menu
			*/
			if (m_settings_menu->calculate_sizes(
				m_padding_data_calculator.get_usable_w(),
				m_padding_data_calculator.get_usable_h()
			) == 1)
				return 1;
			return 0;
			break;
		case 3:
			/*
			 * Settings General Menu
			*/
			if (m_settings_general_menu->calculate_sizes(
				m_padding_data_calculator.get_usable_w(),
				m_padding_data_calculator.get_usable_h()
			) == 1)
				return 1;
			return 0;
			break;
		case 4:
			/*
			 * Settings Graphics Menu
			*/
			if (m_settings_graphics_menu->calculate_sizes(
				m_padding_data_calculator.get_usable_w(),
				m_padding_data_calculator.get_usable_h()
			) == 1)
				return 1;
			return 0;
			break;
		case 5:
			/*
			 * Settings Control Menu
			*/
			if (m_settings_control_menu->calculate_sizes(
				m_padding_data_calculator.get_usable_w(),
				m_padding_data_calculator.get_usable_h()
			) == 1)
				return 1;
			return 0;
			break;
		case 6:
			/*
			 * Settings Sound Menu
			*/
			if (m_settings_sound_menu->calculate_sizes(
				m_padding_data_calculator.get_usable_w(),
				m_padding_data_calculator.get_usable_h()
			) == 1)
				return 1;
			return 0;
			break;
	}
}
int Game::set_gamemode(int gamemode)
{
	std::cout << "set_gamemode(" << gamemode << ") called" << std::endl;
	/*
	 * Uninit old game mode:
	*/
	if (uninit_gamemode(m_gamemode) == 1)
		return 1;
	/*
	 * Init new game mode:
	*/
	if (init_gamemode(gamemode) == 1)
		return 1;
	/*
	 * Set new game mode variable:
	*/
	m_gamemode = gamemode;
	/*
	 * Calculate sizes:
	*/
	calculate_sizes();
	/*
	 * Print status message:
	*/
	std::cout << ">>>> ENTERED GAMEMODE " << m_gamemode << std::endl;
}
int Game::init_gamemode(int gamemode)
{
	switch (gamemode)
	{
		case 1:
			/*
			 * Main Menu
			*/
			m_main_menu = new MainMenu;
			if (m_main_menu->init() == 1)
				return 1;
			return 0;
			break;
		case 2:
			/*
			 * Settings Menu
			*/
			m_settings_menu = new SettingsMenu;
			if (m_settings_menu->init() == 1)
				return 1;
			return 0;
			break;
		case 3:
			/*
			 * Settings General Menu
			*/
			m_settings_general_menu = new SettingsGeneralMenu;
			if (m_settings_general_menu->init() == 1)
				return 1;
			return 0;
			break;
		case 4:
			/*
			 * Settings Graphics Menu
			*/
			m_settings_graphics_menu = new SettingsGraphicsMenu;
			if (m_settings_graphics_menu->init() == 1)
				return 1;
			return 0;
			break;
		case 5:
			/*
			 * Settings Control Menu
			*/
			m_settings_control_menu = new SettingsControlMenu;
			if (m_settings_control_menu->init() == 1)
				return 1;
			return 0;
			break;
		case 6:
			/*
			 * Settings Sound Menu
			*/
			m_settings_sound_menu = new SettingsSoundMenu;
			if (m_settings_sound_menu->init() == 1)
				return 1;
			return 0;
			break;
		default:
			std::cout << "Invalid gamemode passed to init_gamemode(): " << gamemode << std::endl;
			return 1;
	}
}
int Game::uninit_gamemode(int gamemode)
{
	switch (gamemode)
	{
		case 1:
			/*
			 * Main Menu
			*/
			if (m_main_menu->uninit() == 1)
				return 1;
			delete m_main_menu;
			return 0;
			break;
		case 2:
			/*
			 * Settings Menu
			*/
			if (m_settings_menu->uninit() == 1)
				return 1;
			delete m_settings_menu;
			return 0;
			break;
		case 3:
			/*
			 * Settings General Menu
			*/
			if (m_settings_general_menu->uninit() == 1)
				return 1;
			delete m_settings_general_menu;
			return 0;
			break;
		case 4:
			/*
			 * Settings Graphics Menu
			*/
			if (m_settings_graphics_menu->uninit() == 1)
				return 1;
			delete m_settings_graphics_menu;
			return 0;
			break;
		case 5:
			/*
			 * Settings Control Menu
			*/
			if (m_settings_control_menu->uninit() == 1)
				return 1;
			delete m_settings_control_menu;
			return 0;
			break;
		case 6:
			/*
			 * Settings Sound Menu
			*/
			if (m_settings_sound_menu->uninit() == 1)
				return 1;
			delete m_settings_sound_menu;
			return 0;
			break;
		default:
			std::cout << "Invalid gamemode passed to uninit_gamemode(): " << gamemode << std::endl;
			return 0;
	}
}
void Game::draw_main_menu(void)
{
	m_texture.draw(m_main_menu->get_grassblock());
	m_texture.draw(m_main_menu->get_menuitem1());
	m_texture.draw(m_main_menu->get_menuitem1_txt());
	m_texture.draw(m_main_menu->get_menuitem2());
	m_texture.draw(m_main_menu->get_menuitem2_txt());
	m_texture.draw(m_main_menu->get_menuitem3());
	m_texture.draw(m_main_menu->get_menuitem3_txt());
	m_texture.draw(m_main_menu->get_menuitem4());
	m_texture.draw(m_main_menu->get_menuitem4_txt());
	m_texture.draw(m_main_menu->get_menuitem5());
	m_texture.draw(m_main_menu->get_menuitem5_txt());
	m_texture.draw(m_main_menu->get_menuitem6());
	m_texture.draw(m_main_menu->get_menuitem6_txt());
}
void Game::draw_settings_menu(void)
{
	m_texture.draw(m_settings_menu->get_creeper());
	m_texture.draw(m_settings_menu->get_menuitem1());
	m_texture.draw(m_settings_menu->get_menuitem1_txt());
	m_texture.draw(m_settings_menu->get_menuitem2());
	m_texture.draw(m_settings_menu->get_menuitem2_txt());
	m_texture.draw(m_settings_menu->get_menuitem3());
	m_texture.draw(m_settings_menu->get_menuitem3_txt());
	m_texture.draw(m_settings_menu->get_menuitem4());
	m_texture.draw(m_settings_menu->get_menuitem4_txt());
	m_texture.draw(m_settings_menu->get_menuitem5());
	m_texture.draw(m_settings_menu->get_menuitem5_txt());
}
void Game::draw_settings_general_menu(void)
{
	m_texture.draw(m_settings_general_menu->get_menuitem1());
	m_texture.draw(m_settings_general_menu->get_menuitem1_header());
	m_texture.draw(m_settings_general_menu->get_menuitem2());
	m_texture.draw(m_settings_general_menu->get_menuitem2_txt());
}
void Game::draw_settings_graphics_menu(void)
{
	m_texture.draw(m_settings_graphics_menu->get_menuitem1());
	m_texture.draw(m_settings_graphics_menu->get_menuitem1_header());
	m_texture.draw(m_settings_graphics_menu->get_menuitem2());
	m_texture.draw(m_settings_graphics_menu->get_menuitem2_header());
	m_texture.draw(m_settings_graphics_menu->get_menuitem3());
	m_texture.draw(m_settings_graphics_menu->get_menuitem3_txt());
}
void Game::draw_settings_control_menu(void)
{
	/*m_texture.draw(m_settings_control_menu->get_menuitem1());
	m_texture.draw(m_settings_control_menu->get_menuitem1_header());*/
}
void Game::draw_settings_sound_menu(void)
{
	/*m_texture.draw(m_settings_sound_menu->get_menuitem1());
	m_texture.draw(m_settings_sound_menu->get_menuitem1_header());*/
}
