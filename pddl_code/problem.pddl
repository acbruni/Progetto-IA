(defined)
(percept-action pairs
  (percept ?key-location : unknown)
  (action find-key : Effect (and (not ?key-location) (assigns ?key-location to Misty Woods)))
  (action face-wolf : Effect (and (wolf-present?) ?wolf) )
  (action open-door : Effect (if (wolf-present? ?wolf) then (wolf-freed ?wolf) else (door-unlocked)) )
  (action navigate-lighthouse : Effect (if (door-unlocked) then (lighthouse-entered) else (error)))
  (action overcome-traps-illusions : Effect (traps-and-illusions-overcome))
)

(initial facts
  (key-location unknown)
  (wolf-present? false)
  (door-unlocked false)
  (lighthouse-entered false)
)

(goals
  ( recover-lantern ?lantern )
)

(conditions 
  (or 
    (and 
      (find-key) 
      (open-door)) 
    (face-wolf))
)

(defrules 
  (when (not (lighthouse-entered))
    (if ( wolf-freed ?wolf ) then (navigate-lighthouse) else (error) )
  )

(definite-attempts 
  (try to find key)
  (try face wolf)
)

(define (overcome-traps-illusions)
; do something
)

(define (recover-lantern)
; do something
)