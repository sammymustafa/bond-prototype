(function (window) {
    window.extractData = function () {
        var ret = $.Deferred();

        function onError() {
            console.log('Loading error', arguments);
            ret.reject();
        }

        function onReady(smart) {

            if (smart.hasOwnProperty('patient')) {

                var patient = smart.patient;
                var pt = patient.read();
                var cond = smart.patient.api.fetchAll({
                    type: 'Condition',
                    query: {}
                })

                $.when(pt, cond).fail(onError);

                $.when(pt, cond).done(function (patient, conditions) {

                    var gender = patient.gender;
                    var fname = '';
                    var lname = '';
                    var city = patient.address[0].city;
                    var state = patient.address[0].state;
                    var country = patient.address[0].country;

                    if (typeof patient.name[0] !== 'undefined') {
                        fname = patient.name[0].given.join(' ');
                        lname = patient.name[0].family.join(' ');
                    }

                    // Set default patient object
                    var p = defaultPatient();

                    // Patient demographics
                    p.birthdate = patient.birthDate;
                    p.gender = capitalizeFirstLetter(gender);
                    p.city = city;
                    p.state = state;
                    p.country = country;
                    p.fname = fname;
                    p.lname = lname;

                    // Condition
                    p.condition1 = null;
                    p.condition2 = null;
                    p.condition3 = null;
                    p.condition4 = null;
                    p.condition5 = null;
                    if (conditions && conditions.length > 0) {
                        // Collect all unique SNOMED CT coding entries from each condition
                        var allSnomedCodings = [];
                        var uniqueCodes = new Set(); // Use a set to track unique codes
                        
                        conditions.forEach(function(condition) {
                            if (condition.code && condition.code.coding) {
                                condition.code.coding.forEach(function(coding) {
                                    if (coding.system === "http://snomed.info/sct") {
                                        // Check if the code is unique before adding
                                        if (!uniqueCodes.has(coding.code)) {
                                            allSnomedCodings.push(coding);
                                            uniqueCodes.add(coding.code);
                                        }
                                    }
                                });
                            }
                        });
                        // Now assign up to the first 5 SNOMED codes to condition variables or NULL if they don't exist
                        for (var i = 1; i <= 5; i++) {
                            var conditionVar = 'condition' + i;
                            var snomedVar = 'condition' + i + 'snomed';
                            
                            if (allSnomedCodings.length >= i) {
                                p[conditionVar] = allSnomedCodings[i - 1].display;
                                p[snomedVar] = allSnomedCodings[i - 1].code;
                            } else {
                                p[conditionVar] = null; // or use 'NULL' if it needs to be a string
                                p[snomedVar] = null; // or use 'NULL' if it needs to be a string
                            }
                        p.condition1 = allSnomedCodings[0].display;
                        p.condition1snomed = allSnomedCodings[0].code;
                        p.condition2 = allSnomedCodings[1].display;
                        p.condition2snomed = allSnomedCodings[1].code;
                        p.condition3 = allSnomedCodings[2].display;
                        p.condition3snomed = allSnomedCodings[2].code;
                        p.condition4 = allSnomedCodings[3].display;
                        p.condition4snomed = allSnomedCodings[3].code;
                        p.condition5 = allSnomedCodings[4].display;
                        p.condition5snomed = allSnomedCodings[4].code;
                        }
                    }
                    ret.resolve(p);
                });

            }
        }
        FHIR.oauth2.ready(onReady, onError);
        return ret.promise();
    };

    window.downloadPatientData = function(p) {
        var jsonString = JSON.stringify(p);
        var blob = new Blob([jsonString], {type: "application/json"});
        var a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "patient_data.json";
        document.body.appendChild(a); // Append the anchor to body
        a.click(); // Simulate click to download
        document.body.removeChild(a); // Remove the anchor from body
    };


    // Capitalize
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    // Default patient parameters
    function defaultPatient() {

        return {
            fname: { value: '' },
            lname: { value: '' },
            gender: { value: '' },
            birthdate: { value: '' },
            condition1: { value: '' },
            condition1snomed: { value: '' },
            condition2: {value: ''},
            condition2snomed: { value: '' },
            condition3: { value: '' },
            condition3snomed: { value: '' },
            condition4: {value: ''},
            condition4snomed: { value: '' },
            condition5: {value: ''},
            condition5snomed: { value: '' },
            city: { value: '' },
            state: { value: '' },
            country: { value: '' }
        };
    }

    // Draw, show, or hide corresponding HTML on index page
    window.drawVisualization = function (p) {
        $('#holder').show();
        $('#loading').hide();
        $('#fname').html(p.fname);
        $('#lname').html(p.lname);
        $('#gender').html(p.gender);
        $('#birthdate').html(p.birthdate);
        $('#condition1').html(p.condition1);
        $('#condition1snomed').html(p.condition1snomed);
        $('#condition2').html(p.condition2);
        $('#condition2snomed').html(p.condition2snomed);
        $('#condition3').html(p.condition3);
        $('#condition3snomed').html(p.condition3snomed);
        $('#condition4').html(p.condition4);
        $('#condition4snomed').html(p.condition4snomed);
        $('#condition5').html(p.condition5);
        $('#condition5snomed').html(p.condition5snomed);
        $('#city').html(p.city);
        $('#state').html(p.state);
        $('#country').html(p.country);
    };

})(window);