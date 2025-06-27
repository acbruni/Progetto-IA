
(define (domain lantern-of-light)
(:requirements :strips :typing :durative-actions :negative-preconditions)
(:types object location state character item)
(:constants c_init c_goal wolf1 key1 wood lighthouse lantern1 trap1 nowhere
- location
air - state
hero - character)
(:predicates
(inAir ?l - location)(at ?c - character ?l - location)(haveKey ?k - item)
(haveLantern ?l - location)(encounterTrap ?t - object))
(:action navigate
:parameters (?s - state ?d - location)
:precondition (and
(not (inAir c_init))
(at hero c_init)
(not (at hero ?d)))
:effect (and
(not (at hero c_init))
(at hero ?d)
(inAir c_init)))
(:action findKey
:parameters (?k - item)
:precondition (and
(at hero wood)(not (haveKey ?k)))
:effect (and
(haveKey ?k)(not (at hero wood))(inAir c_goal)))
(:action encounterTrap
:parameters (?t - object)
:precondition (encounterTrap ?t)
:effect (not (encounterTrap ?t)))
)
For the problem, we can keep some parts as is and modify others to follow the given plan.