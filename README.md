# jiottranslate
family project: translate MQTT rollershutter commands to two single MQTT relay commands

e.g. 
`cmnd/jviot/B56C52 BLINDSDOWN`
is "converted" to 
`cmnd/sonoff/B56C52/POWER1 OFF` `cmnd/sonoff/B56C52/POWER2 ON`

or
`cmnd/jviot/B56C52 BLINDSSTOP`
to
`cmnd/sonoff/B56C52/POWER1 OFF` `cmnd/sonoff/B56C52/POWER2 OFF`

or
`cmnd/jviot/B56C52 BLINDSUP`
to
`cmnd/sonoff/B56C52/POWER1 ON` `cmnd/sonoff/B56C52/POWER2 OFF`

#Diagram

![diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/miller45/jiottranslat/master/diagram.iuml)