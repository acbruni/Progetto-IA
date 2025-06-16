.Domain
  ; Define types
  (type :adventurer)
  (type :spectral-wolf)
  (type :villager)
  (type :lighthouse-door)
  (type :moon-key)

  ; Define predicates
  (defined-predicate lantern-banished?
    (:param ?x)  // ?x is the location where the Lantern of Light was recovered

    (:precondition
     (not (at ?x lantern-of-light))
     ))

  (defined-predicate wolf-hindered-entry?
    (:param ?x ?y)  // ?x is the location, and ?y is the Wolf

    (:precondition
     (at ?x spectral-wolf)
     (blocker ?x wolf-hinder-entry)

     (:postcondition
      (not (at ?x spectral-wolf))
      ))

  (defined-predicate key-found?
    (:param ?x)  // ?x is the location where the Moon Key was found

    (:precondition
     (empty ?x)
     )

  (defined-predicate lighthouse-door-opened?
    (:param ?x)  // ?x is the location of the enchanted door

    (:precondition
     (at ?x lighthouse-door)
     (key-at ?x moon-key)

     (:postcondition
      (not (blocker ?x wolf-hinder-entry))
      ))

  ; Define actions
  (action ask-grandma-mira
    :parameters (?x)  // ?x is the location to which Grandma Mira will give directions
    :preconditions (at ?x valdombra)
    :effects (in-lights ?x direction))  ; ?direction is the path to take

  (action explore-woods
    :parameters (?x)  // ?x is the location where exploration started
    :preconditions (in-lights ?x misty-woods)
    :effects (key-found ?x))

  (action fight-wolf
    :parameters (?x ?y)  // ?x is the location of the wolf, and ?y is the Wolf
    :preconditions (at ?x spectral-wolf)
    :effects (wolf-hindered-entry ?x))  ; The wolf is no longer hinders entry

  (action unlock-lighthouse-door
    :parameters (?x)  // ?x is the location of the enchanted door
    :preconditions (lighthouse-door-opened?)
    :effects (in-lights ?x lighthouse))

  (action overcome-traps
    :parameters (?x)  // ?x is the location where traps must be overcame

    (:precondition
     (at ?x lighthouse)
     ))

  (action recover-lantern
    :parameters (?x)  // ?x is the location of the Lantern of Light
    :preconditions (in-lights ?x)
    :effects (lantern-banished? ?x))