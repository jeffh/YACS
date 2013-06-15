'use strict';

importScripts(
	'/static/v4/js/lib/underscore-1.4.4.min.js',
	'/static/v4/js/worker/Namespace.js',
	'/static/v4/js/worker/Utils.js',
	'/static/v4/js/worker/ScheduleValidator.js',
);

onmessage = function(msg){
	var response = {type: 'error', reason: 'unknown message type: ' + msg.type};
	if (msg.type === 'conflictsWith') {
		var validator = new Worker.ScheduleValidator(msg.conflicts, msg.sections)
		response = {type: 'return', value: validator.conflictsWith(msg.selection, msg.sectionId)};
	} else if (msg.type === 'isValid') {
		var validator = new Worker.ScheduleValidator(msg.conflicts, msg.sections)
		response = {type: 'return', value: validator.isValid(msg.selection)};
	} else if (msg.type === 'terminate') {
		terminate();
	}
	postMessage(response);
};
