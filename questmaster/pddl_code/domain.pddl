(define (domain lantern-of-light)
(:requirements :strips :typing)
(:types location object person creature key)
(:predicates
(at ?obj - object ?loc - location)
(carrying ?agent - person ?obj - object)
(has-key ?agent - person ?key - key)
(hostile-to ?creature - creature ?location - location)
(hidden-in ?place - location ?object - object)
)
(:action
:parameters (?p - person ?l1 - location ?l2 - location)
:precondition (and (at ?p ?l1)(not(hostile-to ?p ?l2)))
:effect (when (at ?p ?l2) (not (carrying ?p)) (not (at lantern-of-light ?l2))))
(:action
:parameters (?p - person ?k - key ?l - location)
:precondition (and (at ?p ?l)(carrying ?p ?k) (has-key ?p ?k))
:effect (when (not(at ?k ?l)) (at lantern-of-light ?l)))
(:action
:parameters (?p - person ?o - object ?l - location)
:precondition (and (carrying ?p ?o)(hidden-in ?l ?o))
:effect (when (not(at ?o ?l)) (not (hidden-in ?l ?o)))))