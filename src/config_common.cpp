/*
 * config_common.cpp
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
#include "config_common.hpp"

ConfigVariable::ConfigVariable()
{
	
}
ConfigVariable::~ConfigVariable()
{
	
}
Config::Config()
{
	/*
	 * Init default config values:
	*/
	m_vars[0].index = "GENERAL__LANGUAGE";
	m_vars[0].type = CONFIGVAR_TYPE_STRING;
	m_vars[0].value_string = "de";

	m_vars[1].index = "GENERAL__FPSCOUNTER";
	m_vars[1].type = CONFIGVAR_TYPE_BOOLEAN;
	m_vars[1].value_bool = false;
	
	m_vars[2].index = "GRAPHICS__RESOLUTION_X";
	m_vars[2].type = CONFIGVAR_TYPE_INTEGER;
	m_vars[2].value_int = 0;
	
	m_vars[3].index = "GRAPHICS__RESOLUTION_Y";
	m_vars[3].type = CONFIGVAR_TYPE_INTEGER;
	m_vars[3].value_int = 0;
	
	m_vars[4].index = "GRAPHICS__FULLSCREEN";
	m_vars[4].type = CONFIGVAR_TYPE_BOOLEAN;
	m_vars[4].value_bool = true;
	
	m_vars[5].index = "CONTROL__KEY_GOLEFT";
	m_vars[5].type = CONFIGVAR_TYPE_INTEGER;
	m_vars[5].value_int = sf::Keyboard::Left;
	
	m_vars[6].index = "CONTROL__KEY_GORIGHT";
	m_vars[6].type = CONFIGVAR_TYPE_INTEGER;
	m_vars[6].value_int = sf::Keyboard::Right;
	
	m_vars[7].index = "CONTROL__KEY_JUMP";
	m_vars[7].type = CONFIGVAR_TYPE_INTEGER;
	m_vars[7].value_int = sf::Keyboard::Space;

	m_vars[8].index = "SOUND__MENU_MUSIC_VOLUME";
	m_vars[8].type = CONFIGVAR_TYPE_INTEGER;
	m_vars[8].value_int = 100;
	
	m_vars[9].index = "SOUND__GAME_MUSIC_VOLUME";
	m_vars[9].type = CONFIGVAR_TYPE_INTEGER;
	m_vars[9].value_int = 100;
	
	m_vars[10].index = "SOUND__GAME_SOUND_VOLUME";
	m_vars[10].type = CONFIGVAR_TYPE_INTEGER;
	m_vars[10].value_int = 100;
}
Config::~Config()
{
	
}
void Config::dump(void)
{
	/*
	 * Variable declarations:
	*/
	int i;
	std::cout << "== CONFIG DUMP ==" << std::endl;
	/*
	 * Run through variables:
	*/
	for (i=0; i < CONFIGVAR_COUNT; i++)
	{
		std::cout << m_vars[i].index;
		switch (m_vars[i].type)
		{
			case CONFIGVAR_TYPE_INTEGER:
				std::cout << ":int = " << m_vars[i].value_int << std::endl;
				break;
			case CONFIGVAR_TYPE_BOOLEAN:
				if (m_vars[i].value_bool)
					std::cout << ":bool = true" << std::endl;
				else
					std::cout << ":bool = false" << std::endl;
				break;
			case CONFIGVAR_TYPE_STRING:
				std::cout << ":string = " << m_vars[i].value_string << std::endl;
				break;
		}
	}
	std::cout << "== CONFIG DUMP ==" << std::endl;
}
ConfigVariable Config::get(std::string index)
{
	/*
	 * Variable declarations:
	*/
	int i;
	/*
	 * Run through variables:
	*/
	for (i=0; i < CONFIGVAR_COUNT; i++)
	{
		if (m_vars[i].index.compare(index) == 0)
			return m_vars[i];
	}
}
bool Config::set(ConfigVariable var)
{
	std::cout << "Setting ConfigVariable '" << var.index << "'... ";
	/*
	 * Variable declarations:
	*/
	int i;
	/*
	 * Run through variables:
	*/
	for (i=0; i < CONFIGVAR_COUNT; i++)
	{
		if (m_vars[i].index.compare(var.index) == 0)
		{
			m_vars[i] = var;
			std::cout << "[DONE]" << std::endl;
			return true;
		};
	}
	/*
	 * Fallback:
	*/
	std::cout << "[FAIL]" << std::endl;
	return false;
}
