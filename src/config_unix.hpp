/*
 * config_unix.hpp
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
#ifndef _config_unix_hpp_
#	define _config_unix_hpp_
	
#	include <string>
#	include <iostream>
#	include <fstream>
#	include <stdlib.h>
#	include "config_common.hpp"

	
	class Config
	{
		public:
			Config();
			~Config();
			
			/*
			 * Load config:
			*/
			int load(void);
			/*
			 * Write config:
			*/
			int write(void);
			/*
			 * Dump config:
			*/
			void dump(void);
			/*
			 * Get / set variable:
			*/
			ConfigVariable get(std::string index);
			void set(std::string index, ConfigVariable value);
		private:
			ConfigVariable m_vars[CONFIGVAR_COUNT];
	};
#endif // _config_unix_hpp_
