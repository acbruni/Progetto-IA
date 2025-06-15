Here is a valid PDDL (Planning Domain Definition Language) file for this fantasy quest:

```
(define (domain lantern-of-light)
  (:requirements :strips :functions)

  (:types 
    adventurer
    spectral-wolf
    grandma-mira
    misty-woods
    old-lighthouse
    moon-key
    lantern-of-light
    )

  (:predicates 
    (at ?a ?loc)  ; a is at location
    (has-key ?k ?loc)  ; object has key
    (has-lantern ?l ?loc)  ; object has lantern
    (wolf-at ?w ?loc)  ; wolf is at location
    )

  (:functions 
    (find-key)
    (open-door)
    (enter-lighthouse)
    (overcome-traps)
    )

  (:actions 
    (go-to-grandma)
      :parameters (?loc1 ?loc2)
      :preconditions ((at ?a ?loc1) (not (wolf-at spectral-wolf ?loc1)))
      :effects ((at ?a ?loc2))
    )
    (get-directions)
      :parameters (?loc)
      :preconditions ()
      :effects ((has-key misty-woods get-dirs))
    )
    (enter-misty-woods
      :parameters (?d)
      :preconditions ((has-key misty-woods ?d) (not (wolf-at spectral-wolf get-dirs)))
      :effects ((at adventurer misty-woods) (go-to-lighthouse)))
    )
    (find-key
      :parameters (?key)
      :preconditions ((has-key ?key misty-woods))
      :effects ((has-lantern lantern-of-light)))
    )
    (open-door
      :parameters (?door)
      :preconditions ((has-key ?door moon-key) (not (wolf-at spectral-wolf get-dirs)))
      :effects ((at adventurer old-lighthouse) (go-to-lighthouse)))
    )
    (enter-lighthouse
      :parameters ()
      :preconditions ((has-lantern lantern-of-light))
      :effects ((overcome-traps lantern-of-light) (has-lantern lantern-of-light)))
    )
    (avoid-wolf
      :parameters (?wolf)
      :preconditions ((not (at adventurer ?loc)) (wolf-at ?wolf ?loc))
      :effects ((go-to-grandma)))
    )
    )

  (:init-facts 
    (at adventurer valdombra)
    )

  (:goal 
    (at adventurer old-lighthouse) (has-lantern lantern-of-light)

  (:domain-restrictions
  ))

```

This PDDL file defines a domain for the Lantern of Light quest. The `lantern-of-light` domain includes types, predicates, functions, and actions that define the quest.