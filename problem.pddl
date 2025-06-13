; PROBLEM: The Shadow Amulet

; Domain
(domain TheShadowAmulet)

; Objects
(objects
   adventurer - object
   cave - object
   amulet - object
   rune-of-passage - object
   temple - object
   sacred-stone - object
   guardian-golem - object
   secret-door - object)

; Initial State
(init
   (object-at adventurer cave)
   (not (object-at adventurer amulet))
   (not (object-at adventurer guardian-golem))
   (not (object-at adventurer secret-door)))

; Goal
(goal
   (and (object-at adventurer amulet)
        (not (object-at adventurer cave))))

; Preconditions and Effects
(action acquire-amulet
   :parameters (?agent - object)
   :precondition (and (object-at ?agent cave)
                     (not (object-at ?agent amulet))
                     (not (object-at ?agent guardian-golem))
                     (not (object-at ?agent secret-door)))
   :effect (and (object-at ?agent amulet)
                (not (object-at ?agent cave))))

(action activate-rune
   :parameters (?agent - object)
   :precondition (and (object-at ?agent rune-of-passage)
                     (object-on ?agent altar))
   :effect (and (not (object-at ?agent rune-of-passage))
                (object-on ?agent sacred-stone)))

(action enter-cave
   :parameters (?agent - object)
   :precondition (and (object-at ?agent guardian-golem)
                     (not (object-at ?agent rune-of-passage))
                     (not (object-at ?agent secret-door)))
   :effect (and (object-at ?agent cave)
                (not (object-at ?agent guardian-golem))))

(action explore-cave
   :parameters (?agent - object)
   :precondition (and (object-at ?agent cave)
                     (not (object-at ?agent amulet))
                     (not (object-at ?agent golem)))
   :effect (and (object-at ?agent secret-door)
                (not (object-at ?agent cave))))

(action open-secret-door
   :parameters (?agent - object)
   :precondition (and (object-at ?agent amulet)
                     (object-on ?agent sacred-stone))
   :effect (and (not (object-at ?agent amulet))
                (object-at ?agent secret-door)))
```