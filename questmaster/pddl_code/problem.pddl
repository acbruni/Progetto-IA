(define (problemlantern-of-light-problem)
(:domain lantern-of-light)
(:objects
you - person
valdombra - location
mistywoods - location
oldlighthouse - location
grandmamira - person
spectralwolf - creature
lanternoflight - object
moonkey - key
)
(:init
(at you valdombra)
(has-key you moonkey)
(hostile-to spectralwolf valdombra)
(hidden-in mistywoods moonkey)
(carrying you lanternoflight))
(:goal
(and
(not(at spectralwolf valdombra))
(at lanternoflight oldlighthouse)
(not(hostile-to spectralwolf valdombra)))))
