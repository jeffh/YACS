'use strict';

(function(angular, app, undefined){

app.factory('BackgroundWorker', function($q, STATIC_URL){
    return function(conflictObjs, sectionObjs){
        var worker = new Worker(STATIC_URL + 'v4/js/worker/Boot.js');
        worker.postMessage({
            type: 'data',
            conflicts: conflictObjs,
            sections: sectionObjs,
        });
        this.postMessage = function(msg){
            var deferred = $q.defer();
            worker.onmessage = function(msg){
                if (msg.type === 'value'){
                    deferred.resolve(msg.value);
                } else if(msg.type === 'error') {
                    console.error('worker error: ', msg);
                }
            };
            worker.postMessage(_.extend({
                conflicts: conflictObjs,
                sections: sectionObjs
            }, msg));
            return deferred.promise;
        };

        this.conflictsWith = function(selection, sectionId){
            return this.postMessage({
                type: 'conflictsWith',
                selection: selection,
                sectionId: sectionId
            });
        };

        this.isValid = function(selection){
            return this.postMessage({
                type: 'isValid',
                selection: selection
            });
        };

        this.computeSchedules = function(selection, maxNumber){
            return this.postMessage({
                type: 'computeSchedules',
                selection: selection,
                maxNumber: maxNumber
            });
        };
    };
});

})(angular, app);

