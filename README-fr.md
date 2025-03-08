[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacs_badge]][hacs]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

![Icon](https://github.com/jmcollin78/solar_optimizer/blob/main/images/icon.png?raw=true)

> ![Tip](https://github.com/jmcollin78/solar_optimizer/blob/main/images/tips.png?raw=true) Cette intégration permet d'optimiser l'utilisation de votre énergie solaire. Elle commande l'allumage et l'extinction de vos équipements dont l'activation est différable dans le temps en fonction de la production et de la consommation électrique courante.

- [Qu'est-ce que Solar Optimizer ?](#quest-ce-que-solar-optimizer-)
- [Comment fonctionne-t-elle ?](#comment-fonctionne-t-elle-)
  - [Anti-bagot](#anti-bagot)
  - [Utilisabilité](#utilisabilité)
- [Comment on l'installe ?](#comment-on-linstalle-)
  - [HACS installation (recommendé)](#hacs-installation-recommendé)
  - [Installation manuelle](#installation-manuelle)
- [La configuration](#la-configuration)
  - [Configurer l'intégration](#configurer-lintégration)
  - [Configurer les équipements](#configurer-les-équipements)
- [Entités disponibles](#entités-disponibles)
- [En complément](#en-complément)
- [Les contributions sont les bienvenues !](#les-contributions-sont-les-bienvenues)


> ![Nouveau](https://github.com/jmcollin78/solar_optimizer/blob/main/images/new-icon.png?raw=true) _*Nouveautés*_
> * **release 2.1.0** :
>    - ajout d'une durée minimale d'allumage en heure creuses. Permet de gérer les équipements qui doivent avoir un minimum d'allumage par jour comme les chauffes-eau ou les chargeurs (voitures, batteries, ……). Si l'ensoleillement n'a pas durée d'atteindre la durée requise, alors l'équipement s'allumera pendant les heures creuses. Vous pouvez en plus définir à quelle heure les compteurs d'allumage sont remis à zéro ce qui permet de profiter des toutes les heures creuses
> * **release 2.0.0** :
>    - ajout d'un appareil (device) par équipement piloté pour regrouper les entités,
>    - ajout d'un compteur de temps d'allumage pour chaque appareil. Lorsque le switch commandé passe à 'Off', le compteur de temps est incrémenté du temps passé à 'On', en secondes. Ce compteur est remis à zéro tous les jours à minuit.
>    - ajout d'un maximum de temps à 'On' dans la configuration (en minutes). Lorsque cette durée est dépassée, l'équipement n'est plus utilisable par l'algorithme (is_usable = off) jusqu'au prochain reset. Cela offre la possibilité, de ne pas dépasser un temps d'allumage maximal par jour, même lorsque la puissance solaire est disponible.
>    - pour profiter de cette nouvelle info, n'oubliez pas de mettre à jour le decluterring template (en fin de ce fichier)
>    - cette release ouvre la porte a des évolutions plus conséquentes basé sur le temps d'allumage (avoir un minimum journalier par exemple) et prépare le terrain pour l'arrivée de la configuration via l'interface graphique.
* **release 1.7.0** :
  - ajout d'une gestion d'une batterie. Vous pouvez spécifier une entité de type pourcentage qui donne l'état de charge de la batterie (soc). Sur chaque équipements vous pouvez spécifier un paramètre `battery_soc_threshold` : le seuil de batterie en dessous duquel l'équipement ne sera pas utilisable.
* **release 1.3.0** :
  - ajout du paramètre `duration_stop_min` qui permet de spécifier une durée minimale de désactivation pour le distinguer du délai minimal d'activation `duration_min`. Si non spécifié, ce paramètre prend la valeur de `duration_min`.
  - restaure l'état des switchs `enable` au démarrage de l'intégration.
  - lance un calcul immédiatement après le démarrage de Home Assistant
* **release 1.0** : première version opérationnelle. Commande d'équipements basés sur des switchs, commande de puissance (Tesla) et paramétrage via configuration.yaml.

# Qu'est-ce que Solar Optimizer ?
Cette intégration va vous permettre de maximiser l'utilisation de votre production solaire. Vous lui déléguez le contrôle de vos équipements dontl'activation peut être différée dans le temps (chauffe-eau, pompe de piscine, charge de véhicle électrique, lave-vaisselle, lave-linge, etc) et elle s'occupe de les lancer lorsque la puissance produite est suffisante.

Elle tente en permanence de minimiser l'import et l'export d'énergie en démarrant, stoppant, modifiant la puissance allouée à un équipement.

2 types d'équipements sont gérés :
1. les équipements commandés par un switch (un service d'une manière générale) qui ont une puissance consommée fixe et pré-déterminée,
2. les équipements dont la puissance de consommation est réglable (Tesla, Robotdyn). En réglant la puissance allouée à ces équipements, Solar Optimizer aligne la consommation sur la production au plus près.

L'idéal est d'avoir au moins un équipement dont la puissance est ajustable dans la liste des équipements gérés par Solar Optimizer.

# Comment fonctionne-t-elle ?
Le fonctionnement est le suivant :
1. à interval régulier (paramétrable), l'algorithme simule des modifications des états des équipements (allumé / éteint / puissance allouée) et calcule un coût de cette configuration. Globalement le coût est le `a * puissance_importée + b * puissance_exportée`. La coefficients a et b sont calculés en fonction du cout de l'électricité au moment du calcul,
2. l'algorithme garde la meilleure configuration (celle qui a un cout minimum) et cherche d'autres solutions, jusqu'à ce qu'un minimum soit atteint.
3. la meilleure configuration est alors appliquée.

L'algorithme utilisé est un algorithme de type recuit simulé dont vous trouverez une description ici : https://fr.wikipedia.org/wiki/Recuit_simul%C3%A9

## Anti-bagot
Pour éviter les effets de bagottements d'un cycle à l'autre, un délai minimal d'activation est paramétrable par équipements : `duration_min`. Par exemple : un chauffe-eau doit être activé au moins une heure pour que l'allumage soit utile, la charge d'une voiture électrique doit durer au moins deux heures, ...
De façon similaire, une durée minimale de désactivation peut être spécifiée dans le paramètre `duration_stop_min`.

## Utilisabilité
A chaque équipement configuré est associé une entité de type switch qui permet d'autoriser l'algorithme à utiliser l'équipement. Si je veux forcer la chauffe du ballon d'eau chauffe, je mets son switch sur off. L'algorithme ne le regardera donc pas, le chauffe-eau repasse en manuel, non géré par Solar Optimizer.

Par ailleurs, il est possible de définir une règle d'utilisabilité des équipements. Par exemple, si la voiture est chargée à plus de 90%, l'algorithme considère que l'équipement qui pilote la charge de la voiture doit être éteint. Cette régle est définit sous la forme d'un template configurable qui vaut True si l'équipement est utilisable.

Si une batterie est spécifiée lors du paramétrage de l'intégration et si le seuil `battery_soc_threshold` est spécifié, l'équipement ne sera utilisable que si le soc (pourcentage de charge de la batterie) est supérieur ou égal au seuil.

Un temps d'utilisation maximal journalier est paramétrable en facultatif. Si il est valorisé et si la durée d'utilisation de l'équipement est dépasée, alors l'équipement ne sera pas utilisable par l'algorithme et laisse donc de la puissance pour les autres équipements.

Un temps d'utilisation minimal journalier est aussi paramétrable en facultatif. Ce paramètre permet d'assurer que l'équipement sera allumé pendant une certaine durée minimale. Vous spécifiez à quelle heure commence les heures creuses, (`offpeak_time`) et la durée minimale en minutes (`min_on_time_per_day_min`). Si à l'heure indiquée par `offpeak_time`, la durée minimale d'activation n'a pas été atteinte, alors l'équipement est activé jusqu'au changement de jour (paramètrable dans l'intégration et 05:00 par défaut) ou jusqu'à ce que le maximum d'utilisation soit atteint (`max_on_time_per_day_min`) ou pendant toute la durée des heures creuses si `max_on_time_per_day_min` n'est pas précisé. Vous assurez ainsi que le chauffe-eau ou la voiture sera chargée le lendemain matin même si la production solaire n'a pas permise de recharger l'appareil. A vous d'inventer les usages de cette fonction.

Ces 5 règles permettent à l'algorithme de ne commander que ce qui est réellement utile à un instant t. Ces règles sont ré-évaluées à chaque cycle.

# Comment on l'installe ?
## HACS installation (recommendé)

1. Installez [HACS](https://hacs.xyz/). De cette façon, vous obtenez automatiquement les mises à jour.
2. Ajoutez ce repository Github en tant que repository personnalisé dans les paramètres HACS.
3. recherchez et installez "Solar Optimizer" dans HACS et cliquez sur "installer".
4. Redémarrez Home Assistant.
5. Ensuite, vous pouvez ajouter l'intégration de Solar Optimizer dans la page d'intégration. Vous ne pouvez installer qu'une seule intégration Solar Optimizer.

## Installation manuelle
Une installation manuelle est possible. Elle n'est pas recommandée et donc elle ne sera pas décrite ici.

# La configuration
## Configurer l'intégration
Lors de l'ajout de l'intégration Solar Optimizer, la page de paramétrage suivante s'ouvre :

Vous devez spécifier :
1. le sensor qui donne la consommation nette instantanée du logement (elle doit être négative si la production dépasse la consommation). Ce chiffre est indiqué en Watt,
2. le sensor qui donne la production photovoltaïque instantanée en Watt aussi (elle est forcément positive ou nulle),
3. un sensor ou input_number qui donne le cout du kwh importée (requis: nombre strictement positif),
4. un sensor ou input_number qui donne le prix du kwh exportée (requis: nombre strictement positif)(dépend de votre contrat), on peut utiliser la même valeur/sensor que l'importée si pas de contrat de revente,
5. un sensor ou input_number qui donne la taxe applicable sur les kwh exportée (chiffre positif ou 0) (dépend de votre contrat)
6. l'heure de début de journée. A cette heure les compteurs d'uitlisation des équipements sont remis à zéro. La valeur par défaut est 05:00. Elle doit être avant la première production et le plus tard possible pour les activations en heures creuses. Cf. ci-dessus.


Ces 5 informations sont nécessaires à l'algorithme pour fonctionner, elles sont donc toutes obligatoires. Le fait que ce soit des sensor ou input_number permet d'avoir des valeurs qui sont réévaluées à chaque cycle. En conséquence le passage en heure creuse peut modifier le calcul et donc les états des équipements puisque l'import devient moins cher. Donc tout est dynamique et recalculé à chaque cycle.

## Configurer les équipements
Les équipements pilotables sont définis dans le fichier configuration.yaml de la façon suivante :
- ajouter la ligne suivante dans votre configuration.yaml:

  ```solar_optimizer: !include solar_optimizer.yaml```
- et créez un fichier au même niveau que le configuration.yaml avec les informations suivantes :
```
algorithm:
  initial_temp: 1000
  min_temp: 0.1
  cooling_factor: 0.95
  max_iteration_number: 1000
devices:
  - name: "<nom de l'équipement>"
    entity_id: "switch.xxxxx"
    power_max: <puissance max consommée>
    check_usable_template: "{{ <le template qui vaut True si l'équipement est utilisable> }}"
    duration_min: <la durée minimale d'activation en minutes>
    duration_stop_min: <la durée minimale de desactivation en minutes>
    action_mode: "action_call"
    activation_service: "<service name>
    deactivation_service: "switch/turn_off"
    battery_soc_threshold: <l'état de charge minimal pour utiliser cet équipement>
    max_on_time_per_day_min: <la durée maximamle d'allumage par jour en minutes>
    offpeak_time: <l'heure de début des heures creuses>
    min_on_time_per_day_min: <la durée minimale d'allumage par jour en minutes>
```

Note: les paramètres sous `algorithm` ne doivent pas être touchés sauf si vous savez exactement ce que vous faites.

Sous `devices` il faut déclarer tous les équipements qui seront commandés par Solar Optimizer de la façon suivante :

| attribut                  | valable pour                            | signification                                                                                                                                                                                                                                | exemple                                                 | commentaire                                                                                                                                                                          |
| ------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`                    | tous                                    | Le nom de l'équipement                                                                                                                                                                                                                       | "VMC sous-sol"                                          | -                                                                                                                                                                                    |
| `entity_id`               | tous                                    | l'entity id de l'équipement à commander                                                                                                                                                                                                      | "switch.vmc_sous_sol"                                   | -                                                                                                                                                                                    |
| `power_max`               | tous                                    | la puissance maximale consommée par l'équipement                                                                                                                                                                                             | 250                                                     | -                                                                                                                                                                                    |
| `check_usable_template`   | tous                                    | Un template qui vaut True si l'équipement pourra être utilisé par Solar Optimizer                                                                                                                                                            | "{{ is_state('cover.porte_garage_garage', 'closed') }}" | Dans l'exemple, Sonar Optimizer n'essayera pas de commander la "VMC sous-sol" si la porte du garage est ouverte                                                                      |
| `duration_min`            | tous                                    | La durée en minute minimale d'activation                                                                                                                                                                                                     | 60                                                      | La VMC sous-sol s'allumera toujours pour une heure au minimum                                                                                                                        |
| `duration_stop_min`       | tous                                    | La durée en minute minimale de desactivation. Vaut `duration_min` si elle n'est pas précisée                                                                                                                                                 | 15                                                      | La VMC sous-sol s'éteindra toujours pour 15 min au minimum                                                                                                                           |
| `action_mode`             | tous                                    | le mode d'action pour allumer ou éteindre l'équipement. Peut être "action_call" ou "event" (*)                                                                                                                                               | "action_call"                                           | "action_call" indique que l'équipement s'allume et s'éteint via un appel de service. Cf. ci-dessous. "event" indique qu'un évènement est envoyé lorsque l'état doit changer. Cf. (*) |
| `activation_service`      | uniquement si action_mode="action_call" | le service a appeler pour activer l'équipement sous la forme "domain/service"                                                                                                                                                                | "switch/turn_on"                                        | l'activation déclenchera le service "switch/turn_on" sur l'entité "entity_id"                                                                                                        |
| `deactivation_service`    | uniquement si action_mode="action_call" | le service a appeler pour désactiver l'équipement sous la forme "domain/service"                                                                                                                                                             | "switch/turn_off"                                       | la désactivation déclenchera le service "switch/turn_off" sur l'entité "entity_id"                                                                                                   |
| `battery_soc_threshold`   | tous                                    | le pourcentage minimal de charge de la batterie pour que l'équipement soit utilisable                                                                                                                                                        | 30                                                      |                                                                                                                                                                                      |
| `max_on_time_per_day_min` | tous                                    | le nombre de minutes maximal en position allumé pour cet équipement. Au delà, l'équipement n'est plus utilisable par l'algorithme                                                                                                            | 10                                                      | L'équipement est sera allumé au maximum 10 minutes par jour                                                                                                                          |
| `offpeak_time`            | tous                                    | L'heure de début des heures creuses au format hh:mm                                                                                                                                                                                          | "22:00"                                                 | L'équipement pourra être allumé à 22h00 si la production de la journeé n'a pas été suffisante                                                                                        |
| `min_on_time_per_day_min` | tous                                    | le nombre de minutes minimale en position allumé pour cet équipement. Si lors du démarrage des heures creuses, ce minimum n'est pas atteint alors l'équipement sera allumé à concurrence du début de journée ou du `max_on_time_per_day_min` | 5                                                       | L'équipement est sera allumé au minimum 5 minutes par jour                                                                                                                           |

Pour les équipements à puissance variable, les attributs suivants doivent être valorisés :

| attribut                      | valable pour                    | signification                                                 | exemple                      | commentaire                                                                                                                                                                                                                                                                                              |
| ----------------------------- | ------------------------------- | ------------------------------------------------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `power_entity_id`             | équipement à puissance variable | l'entity_id de l'entité gérant la puissance                   | `number.tesla_charging_amps` | Le changement de puissance se fera par un appel du service `change_power_service` sur cette entité                                                                                                                                                                                                       |
| `power_min`                   | équipement a puissance variable | La puissance minimale en watt de l'équipement                 | 100                          | Lorsque la consigne de puissance passe en dessous de cette valeur, l'équipement sera éteint par l'appel du `deactivation_service`                                                                                                                                                                        |
| `power_step`                  | équipement a puissance variable | Le pas de puissance                                           | 10                           | -                                                                                                                                                                                                                                                                                                        |
| `change_power_service`        | équipement a puissance variable | Le service a appelé pour changer la puissance                 | `"number/set_value"`         | -                                                                                                                                                                                                                                                                                                        |
| `convert_power_divide_factor` | équipement a puissance variable | Le diviseur a appliquer pour convertir la puissance en valeur | 50                           | Dans l'exemple, le service "number/set_value" sera appelé avec la `consigne de puissance / 50` sur l'entité `entity_id`. Pour une Tesla sur une installation tri-phasée, la valeur est 660 (220 v x 3) ce qui permet de convertir une puissance en ampère. Pour une installation mono-phasé, mettre 220. |

Exemple complet et commenté de la partie device :
```
devices:
  - name: "Pompe réservoir"
    # Le switch qui commande la pompe du réservoir
    entity_id: "switch.prise_pompe_reservoir"
    # la puissance de cette pompe
    power_max: 170
    # Toujours utilisable
    # check_usable_template: "{{ True }}"
    # 15 min d'activation minimum
    duration_min: 15
    # 5 min de desactivation minimum
    duration_stop_min: 5
    # On active/desactive via un appel de service
    action_mode: "action_call"
    # Le service permettant d'activer le switch
    activation_service: "switch/turn_on"
    # Le service permettant de désactiver le switch
    deactivation_service: "switch/turn_off"
    # On autorise le démarrage de la pompe si il y a 10% de batterie dans l'installation solaire
    battery_soc_threshold: 10
    # Une heure par jour maximum
    max_on_time_per_day_min: 60
    # 1/2h par jour minimum ...
    min_on_time_per_day_min: 30
    # ... à partir de 22:30
    offpeak_time: "22:30"

  - name: "Recharge Tesla"
    entity_id: "switch.testla_charger"
    # La puissance minimale de charge est 660 W (soit 1 Amp car convert_power_divide_factor=660 aussi)
    power_min: 660
    # La puissance minimale de charge est 3960 W (soit 5 Amp (= 3960/600) )
    power_max: 3960
    # le step de 660 soit 1 Amp après division par convert_power_divide_factor
    power_step: 660
    # Utilisable si le mode de charge est "Solaire" et la voiture est branchée sur le chargeur et elle est chargée à moins de 90 % (donc ca s'arrête tout seul à 90% )
    check_usable_template: "{{ is_state('input_select.charge_mode', 'Solaire') and is_state('binary_sensor.tesla_wall_connector_vehicle_connected', 'on') and is_state('binary_sensor.tesla_charger', 'on') and states('sensor.tesla_battery') | float(100) < states('number.tesla_charge_limit') | float(90) }}"
    # 1 h de charge minimum
    duration_min: 60
    # 15 min de stop charge minimum
    duration_stop_min: 15
    # L'entité qui pilote l'ampérage de charge
    power_entity_id: "number.tesla_charging_amps"
    # 5 min minimum entre 2 changements de puissance
    duration_power_min: 5
    # l'activation se fait par un appel de service
    action_mode: "action_call"
    activation_service: "switch/turn_on"
    deactivation_service: "switch/turn_off"
    # le changement de puissance se fait par un appel de service
    change_power_service: "number/set_value"
    # le facteur permettant de convertir la puissance consigne en Ampères (number.tesla_charging_amps prend des Ampères)
    convert_power_divide_factor: 660
    # On ne démarre pas une charge si la batterie de l'installation solaire n'est pas chargée à au moins 50%
    battery_soc_threshold: 50
    # 4h par jour minimum ...
    min_on_time_per_day_min: 240
    # ... à partir de 23:00
    offpeak_time: "22:00"
...
```
Tout changement dans la configuration nécessite un arrêt / relance de l'intégration (ou de Home Assistant) pour être pris en compte.

# Entités disponibles
L'intégration, une fois correctement configurée, créée un appareil (device) qui contient plusieurs entités :
1. un sensor nommé "total_power" qui est le total de toutes les puissances des équipements commandés par Solar Optimizer,
2. un sensor nommé "best_objective" qui est la valeur de la fonction de coût (cf. fonctionnement de l'algo),
3. un switch par équipements nommé `switch.enable_solar_optimizer_<name>` déclarés dans le configuration.yaml. Si le switch est "Off", l'algorithme ne considérera pas cet équipement pour le calcul. Ca permet de manuellement sortir un équipement de la liste sans avoir à modifier la liste. Ce switch contient des attributs additionnels qui permettent de suivre l'état interne de l'équipement vu de l'algorithme.

# Une carte pour vos dashboard en complément
En complément, les codessuivant Lovelace suivant permet de controller chaque équipement déclaré.
Les étapes à suivre sont :
1. Avec HACS, installez les plugins nommés `streamline-card`, `expander-card` et `mushroom-template` si vous ne les avez pas déjà,
2. Installez les templates pour `streamline` en tête de votre code Lovelace,
3. Installez une carte par équipement géré par Solar Optimizer qui référence le template `streammline``

## Installez les plugins
Lisez la documentation du plugin [ici](https://github.com/brunosabot/streamline-card) pour vous familiariser avec cet excellent plugin.
Suivez la procédure d'installation qui consiste à installer un nouveau dépôt Github de type `Dashboard` et à installer le plugin.

Vous devez avoir dans la partie "Téléchargé" vos plugins de visibles :

![HACS Plugin](images/install-hacs-streamline.png)

Faites de même avec les plugins `expander-card` et `mushroom-template`.

## Installez les templates
Pour installer les templates vous devez aller sur votre dashboard, vous mettre en édition et cliquer sur les trois points dans le menu en haut à droite :

![dahsboard edit](images/dashboard-edit.png)

puis

![dashboard edit 2](images/dashboard-edit2.png)

puis

![dashboard edit 3](images/dashboard-edit3.png)

Vous arrivez alors en édition manuelle de votre dashboard Lovelace.

Attention : le yaml est susceptible. L'indentation doit être scrupuleusement respectée.

Copier/coller le texte ci-dessous (cliquez sur le bouton copier pour tout prendre sans risque) tout au début 1 ligne, 1 colonne.

```yaml
# A mettre en début de page sur le front
streamline_templates:
  managed_device_power:
    default: null
    card:
      type: custom:expander-card
      expanded: false
      title-card-button-overlay: true
      title-card:
        type: custom:mushroom-template-card
        primary: '{{ state_attr(''[[device]]'', ''device_name'') }}'
        secondary: >-
          [[secondary_infos]] ({{ state_attr('[[on_time_entity]]',
          'on_time_hms') }} / {{ state_attr('[[on_time_entity]]',
          'max_on_time_hms')}} )
        icon: '[[icon]]'
        badge_icon: >-
          {% if is_state_attr('[[on_time_entity]]','should_be_forced_offpeak',
          True) %}mdi:power-sleep{% elif
          is_state_attr('[[device]]','is_enabled', True) %}mdi:check{% else
          %}mdi:cancel{% endif %}
        badge_color: >-
          {% if is_state_attr('[[on_time_entity]]','should_be_forced_offpeak',
          True) %}#003366{% elif is_state_attr('[[device]]', 'is_usable', True)
          and is_state_attr('[[device]]', 'is_enabled', True) %}green {% elif
          is_state_attr('[[device]]', 'is_enabled', False) %}red {% elif
          is_state_attr('[[device]]','is_waiting', True) %}orange {% elif
          is_state_attr('[[device]]', 'is_usable', False) or
          state_attr('[[device]]', 'is_usable') is none %}#A0B0FF{% else
          %}blue{% endif %}
        entity: '[[device]]'
        icon_color: >-
          {% if is_state('[[device]]', 'on')%}orange{% else %}lightgray{% endif
          %}
        tap_action:
          action: toggle
        hold_action:
          action: more-info
        double_tap_action:
          action: none
      cards:
        - type: custom:mushroom-chips-card
          chips:
            - type: entity
              entity: '[[enable_entity]]'
              double_tap_action:
                action: more-info
              tap_action:
                action: toggle
              hold_action:
                action: more-info
              icon_color: green
              content_info: name
        - type: markdown
          content: >-
            **Prochaine dispo** : {{ ((as_timestamp(state_attr('[[device]]',
            'next_date_available')) - as_timestamp(now())) / 60) | int }}
            min<br> **Prochaine dispo puissance**: {{
            ((as_timestamp(state_attr('[[device]]',
            'next_date_available_power')) - as_timestamp(now())) / 60) | int }}
            min<br> **Utilisable** : {{ state_attr('[[device]]', 'is_usable')
            }}<br> **Est en attente**  : {{ state_attr('[[device]]',
            'is_waiting') }}<br> **Est forcé en heures creuses**  : {{
            state_attr('[[on_time_entity]]', 'should_be_forced_offpeak') }}<br>
            **Heures creuses**  : {{ state_attr('[[on_time_entity]]',
            'offpeak_time') }}<br> **Puissance requise** : {{
            state_attr('[[device]]', 'requested_power') }} W<br> **Puissance
            courante** : {{ state_attr('[[device]]', 'current_power') }} W
          title: Infos
        - type: history-graph
          hours: 24
          entities:
            - entity: '[[device]]'
            - entity: '[[enable_entity]]'
            - entity: '[[power_entity]]'
  managed_device:
    default: null
    card:
      type: custom:expander-card
      expanded: false
      title-card-button-overlay: true
      title-card:
        type: custom:mushroom-template-card
        primary: '{{ state_attr(''[[device]]'', ''device_name'') }}'
        secondary: >-
          [[secondary_infos]] (max. {{ state_attr('[[device]]', 'power_max') }}
          W -  {{ state_attr('[[on_time_entity]]', 'on_time_hms')}} / {{
          state_attr('[[on_time_entity]]', 'max_on_time_hms')}} )
        icon: '[[icon]]'
        badge_icon: >-
          {% if is_state_attr('[[on_time_entity]]','should_be_forced_offpeak',
          True) %}mdi:power-sleep{% elif
          is_state_attr('[[device]]','is_enabled', True) %}mdi:check{% else
          %}mdi:cancel{% endif %}
        badge_color: >-
          {% if is_state_attr('[[on_time_entity]]','should_be_forced_offpeak',
          True) %}#003366{% elif is_state_attr('[[device]]', 'is_usable', True)
          and is_state_attr('[[device]]', 'is_enabled', True) %}green {% elif
          is_state_attr('[[device]]', 'is_enabled', False) %}red {% elif
          is_state_attr('[[device]]','is_waiting', True) %}orange {% elif
          is_state_attr('[[device]]', 'is_usable', False) or
          state_attr('[[device]]', 'is_usable') is none %}#A0B0FF{% else
          %}blue{% endif %}
        entity: '[[device]]'
        icon_color: >-
          {% if is_state('[[device]]', 'on')%}orange{% else %}lightgray{% endif
          %}
        tap_action:
          action: toggle
        hold_action:
          action: more-info
        double_tap_action:
          action: none
      cards:
        - type: custom:mushroom-chips-card
          chips:
            - type: entity
              entity: '[[enable_entity]]'
              double_tap_action:
                action: more-info
              tap_action:
                action: toggle
              hold_action:
                action: more-info
              icon_color: green
              content_info: name
        - type: markdown
          content: >-
            **Prochaine dispo** : {{ ((as_timestamp(state_attr('[[device]]',
            'next_date_available')) - as_timestamp(now())) / 60) | int }}
            min<br> **Utilisable** : {{ state_attr('[[device]]', 'is_usable')
            }}<br> **Est en attente**  : {{ state_attr('[[device]]',
            'is_waiting') }}<br> **Est forcé en heures creuses**  : {{
            state_attr('[[on_time_entity]]', 'should_be_forced_offpeak') }}<br>
            **Heures creuses**  : {{ state_attr('[[on_time_entity]]',
            'offpeak_time') }}<br> **Puissance requise** : {{
            state_attr('[[device]]', 'requested_power') }} W<br> **Puissance
            courante** : {{ state_attr('[[device]]', 'current_power') }} W
        - type: history-graph
          hours: 24
          entities:
            - entity: '[[device]]'
            - entity: '[[enable_entity]]'
            - entity: '[[power_entity]]'
```

Vous devez avoir une page qui ressemble à ça :

![dashboard edit 4](images/dashboard-edit4.png)

Cliquez alors sur Enregistrer puis Terminer. Les templates sont maintenant installés, il ne reste plus qu'à les utiliser.

## Ajoutez une carte par équipements

Pour utiliser les templates installés à l'étape précédente, vous devez :
1. Editer un dashboard ou vous voulez ajouter la carte,
2. cliquer sur 'Ajouter une carte' en bas à droite,
3. sélectionner la carte nommée Streamline Card comme ceci :

![dashboard edit 4](images/add-card-1.png)

4. remplir les champs de la façon suivante :

![dashboard edit 4](images/add-card-2.png)

Vous devez choisir le template `managed_device` pour un équipement non muni d'une modulation de puissance ou `managed_device_power` sinon.
Saisissez ensuite les différents attributs.
Un exemple complet pour un équipement 'non power' :

![dashboard edit 4](images/add-card-3.png)

et pour un équipement avec modulation de puissance :

![dashboard edit 4](images/add-card-4.png)

Vous obtiendrez alors un composant permettant d'interagir avec l'équipement qui ressemble à ça :

![Lovelace equipements](https://github.com/jmcollin78/solar_optimizer/blob/main/images/lovelace-eqts.png?raw=true)

## Utilisation de la carte
La carte ainsi obtenue permet de voir l'état d'utilisation de l'équipement et d'interagir avec lui. Ouvrez la carte en appuyant sur le 'V' et vous obtenez ça :

![use card 1](images/use-card-1.png)

### Couleur de l'icône

| Couleur | Signification     | Exemple                              |
| ------- | ----------------- | ------------------------------------ |
| Gris    | Equipement éteint | ![use card 2](images/use-card-2.png) |
| Jaune   | Equipement allumé | ![use card 3](images/use-card-3.png) |

### Badge

| Icone / Couleur  | Signification                                                      | Exemple                                         |
| ---------------- | ------------------------------------------------------------------ | ----------------------------------------------- |
| Coche verte      | Equipement éteint en attente de production                         | ![use card 4](images/use-card-green-check.png)  |
| Coche bleue      | Equipement éteint non disponible (`check-usable` renvoie faux)     | ![use card 4](images/use-card-blue-check.png)   |
| Coche orange     | Equipement éteint en attente du délai enttre 2                     | ![use card 4](images/use-card-orange-check.png) |
| Annulation rouge | Equipement éteint non autorisé par l'utilisation `enable` est faux | ![use card 4](images/use-card-red-cancel.png)   |
| Lune Bleu nuit   | Equipement allumé en heures creuses                                | ![use card 4](images/use-card-blue-moon.png)    |

### Action sur la carte
Cliquez sur la carte de l'équipement et ça forcera son allumage ou son extinction.
Cliquez sur le bouton `Enable` et ça autorisera ou non l'utilisation de l'équipement par l'algorithme de Solar Optimizer.

# Les contributions sont les bienvenues !

Si vous souhaitez contribuer, veuillez lire les [directives de contribution](CONTRIBUTING.md)

***

[solar_optimizer]: https://github.com/jmcollin78/solar_optimizer
[buymecoffee]: https://www.buymeacoffee.com/jmcollin78
[buymecoffeebadge]: https://img.shields.io/badge/Buy%20me%20a%20beer-%245-orange?style=for-the-badge&logo=buy-me-a-beer
[commits-shield]: https://img.shields.io/github/commit-activity/y/jmcollin78/solar_optimizer.svg?style=for-the-badge
[commits]: https://github.com/jmcollin78/solar_optimizer/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacs_badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://forum.hacf.fr/
[license-shield]: https://img.shields.io/github/license/jmcollin78/solar_optimizer.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Joakim%20Sørensen%20%40ludeeus-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/jmcollin78/solar_optimizer.svg?style=for-the-badge
[releases]: https://github.com/jmcollin78/solar_optimizer/releases
