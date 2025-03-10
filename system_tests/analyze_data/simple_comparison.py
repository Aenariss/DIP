#
#  Copyright (C) 2020  Martin Bednar
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

## Check if log was added by extension. Check with Simple method (equality of text strings).
def was_log_added(log, logs_without_addon):
    for log_without_addon in logs_without_addon:
        if log_without_addon['level'] == log['level']:
            if log_without_addon['source'] == log['source']:
                if log_without_addon['message'] == log['message']:
                    return False
    return True
