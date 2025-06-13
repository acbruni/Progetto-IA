; DOMAIN: The Shadow Amulet

; Requirements
:requirements :strips :typing :adl :conditional-effects :negative-preconditions

; Types
; Define a simple hierarchy of types
(types object)
(type cave object)
(type amulet object)
(type rune-of-passage object)
(type temple object)
(type sacred-stone object)
(type guardian-golem object)
(type secret-door object)

; Actions
; Define the actions available in the domain
(actions acquire-amulet
   :parameters (?agent - object)
   :precondition (and (object-at ?agent cave)
                     (not (object-at ?agent amulet))
                     (not (object-at ?agent guardian-golem))
                     (not (object-at ?agent secret-door)))
   :effect (and (object-at ?agent amulet)
                (not (object-at ?agent cave))))

(actions activate-rune
   :parameters (?agent - object)
   :precondition (and (object-at ?agent rune-of-passage)
                     (object-on ?agent altar))
   :effect (and (not (object-at ?agent rune-of-passage))
                (object-on ?agent sacred-stone)))

(actions enter-cave
   :parameters (?agent - object)
   :precondition (and (object-at ?agent guardian-golem)
                     (not (object-at ?agent rune-of-passage))
                     (not (object-at ?agent secret-door)))
   :effect (and (object-at ?agent cave)
                (not (object-at ?agent guardian-golem))))

(actions explore-cave
   :parameters (?agent - object)
   :precondition (and (object-at ?agent cave)
                     (not (object-at ?agent amulet))
                     (not (object-at ?agent golem)))
   :effect (and (object-at ?agent secret-door)
                (not (object-at ?agent cave))))

(actions open-secret-door
   :parameters (?agent - object)
   :precondition (and (object-at ?agent amulet)
                     (object-on ?agent sacred-stone))
   :effect (and (not (object-at ?agent amulet))
                (object-at ?agent secret-door)))
```
Il file di problema PDDL generato è il seguente:
```