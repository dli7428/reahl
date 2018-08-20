/* Copyright 2013-2018 Reahl Software Services (Pty) Ltd. All rights reserved. */
/*
    This file is part of Reahl.

    Reahl is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation; version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/


(function($) {
"use strict";

$.widget('reahl.hashchange', {
    options: {
            url: '',
            cache: true,
            errorMessage: 'Ajax error',
            timeoutMessage: 'Ajax timeout',
            params: []
    },

    _create: function() {
        var o = this.options;
        var element = this.element;
        var _this = this;

        _this.options.previousHashValues = $.extend(true, {}, _this.options.params);
        $(window).on( 'hashchange', function(e) {
            var allCurrentHashValues = e.getState();
            var changedRelevantHashValues = _this.calculateChangedRelevantHashValues(allCurrentHashValues);
            if (_this.hasChanged(changedRelevantHashValues)) {
                _this.triggerChange(allCurrentHashValues, changedRelevantHashValues);
            };
            return true;
        });
        
        $(window).trigger( 'hashchange' );
    },
    getIsList: function(name) {
        return name.match('\\[\\]$');
    },
    getCleanName: function(name) {
        if (this.getIsList(name)) {
            return name.match('(.*)\\[\\]$')[1];
        } else {
            return name;
        }
    },
    getEmptyListSentinel: function(name) {
        return name+'-';
    },
    triggerChange: function(allCurrentHashValues, changedRelevantHashValues) {
        var _this = this;
        var allNewHashValues = $.extend({}, allCurrentHashValues);

        for (var name in _this.options.previousHashValues) {
            var cleanName = _this.getCleanName(name);
            if (!allNewHashValues[cleanName]) {
                var emptySentinelName = name+'-';
                if (_this.getIsList(name) && allNewHashValues[emptySentinelName]) {
                    allNewHashValues[emptySentinelName] = ""; 
                } else {
                    allNewHashValues[cleanName] = _this.options.previousHashValues[name]; 
                }
            }
        };
        
        var loading = _this.element.block({overlayCSS: {backgroundColor: '#fff', opacity: 0.3}, message: '', fadeIn: 0, fadeout: 0});
        $.ajax({url:     _this.options.url,
                cache:   _this.options.cache,
                data:    allNewHashValues,
                success: function(data){
                    _this.element.html(data);
                    _this.options.previousHashValues = changedRelevantHashValues;
                },
                complete: function(data){
                    _this.element.unblock();
                },
                traditional: false
        });
    },
    hasChanged: function(newRelevantHashValues){
        var _this = this;
        var changed = false;
        for (var name in _this.options.previousHashValues) {
            if ( ! _.isEqual(newRelevantHashValues[name], _this.options.previousHashValues[name])) {
                changed = true;
            };
            if (_this.getIsList(name)) {
                var emptySentinelName = _this.getEmptyListSentinel(name);
                if (!_.isEqual(newRelevantHashValues[emptySentinelName], _this.options.previousHashValues[emptySentinelName])) {
                    changed = true;
                }
            }
        };
        return changed;
    },
    calculateChangedRelevantHashValues: function(allCurrentHashValues) {
        var _this = this;
        var changedRelevantHashValues = {};
        for (var name in _this.options.previousHashValues) {
            var cleanName = _this.getCleanName(name);
            var currentValue = allCurrentHashValues[cleanName];
            if (currentValue) {
                changedRelevantHashValues[name]=currentValue;
            } else if (_this.getIsList(name)) {
                var emptySentinelName = _this.getEmptyListSentinel(name);
                if (allCurrentHashValues[emptySentinelName] != undefined) {
                    changedRelevantHashValues[emptySentinelName] = "";
                } else {
                    changedRelevantHashValues[name]=_this.options.previousHashValues[name];
                }
            } else {
                changedRelevantHashValues[name]=_this.options.previousHashValues[name];
            }
        };
        return changedRelevantHashValues;
    },
});

$.extend($.reahl.hashchange, {
    version: '1.8'
});

})(jQuery);


