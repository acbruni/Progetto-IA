(define (problemlantern-of-light-problem)
(:domain lantern-of-light)
(:objects
wood lighthouse lantern1 key1 - object
c_init c_goal nowhere air lit unlit - state
hero - character)
(:init
(at hero wood)(haveKey key1)(encounterTrap trap1)(inAir nothing))
(:goal (and
(not (haveKey key1))
(not (encounterTrap trap1))
(at hero lighthouse)
(haveLantern lantern1)))
(:metric minimize (distanceToGoal))
)