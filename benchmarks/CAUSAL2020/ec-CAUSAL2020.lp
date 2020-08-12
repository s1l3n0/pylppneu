% Event Calculus axioms 
holdsAt(F, P, N) :-
  initially(F, P),
  not clipped(0, F, P, N),
  fluent(F), place(P), time(N).

holdsAt(F, P, N2) :-
  firesAt(T, N1), N1 < N2,
  initiates(T, F, P, N1),
  not clipped(N1, F, P, N2),
  place(P), transition(T), fluent(F), time(N1), time(N2).

clipped(N1, F, P, N2) :-
  firesAt(T, N), N1 <= N, N < N2,
  terminates(T, F, P, N),
  place(P), transition(T), fluent(F), time(N1), time(N2), time(N).

% Operational axioms 
{prefiresAt(T, N)} :-
  enabled(T, N), transition(T), time(N).

someTransitionPrefiresAt(N) :-
  prefiresAt(T, N), transition(T), time(N).

:- not someTransitionPrefiresAt(0).
:- N > 0, not someTransitionPrefiresAt(N - 1), time(N).
:- prefiresAt(T1, N), prefiresAt(T2, N), T1 != T2, transition(T1), transition(T2), time(N).

% Places 
fluent(filled).

place(c1). initially(filled, c1).
:- 2{terminates(e2, filled, c1, N); terminates(e1, filled, c1, N)}.

place(c2).
place(c3).
place(c4). initially(filled, c4).
place(c5).

% Transitions 
transition(e1).
enabled(e1, N) :- holdsAt(filled, c1, N).
firesAt(e1, N) :- prefiresAt(e1, N).
terminates(e1, filled, c1, N) :- firesAt(e1, N).
initiates(e1, filled, c2, N) :- firesAt(e1, N).

transition(e2).
enabled(e2, N) :- holdsAt(filled, c1, N).
firesAt(e2, N) :- prefiresAt(e2, N).
terminates(e2, filled, c1, N) :- firesAt(e2, N).

transition(e3).
enabled(e3, N) :- holdsAt(filled, c4, N).
firesAt(e3, N) :- prefiresAt(e3, N).
terminates(e3, filled, c4, N) :- firesAt(e3, N).
initiates(e3, filled, c3, N) :- firesAt(e3, N).

% Bindings on places 
holdsAt(filled, c5, N) :- holdsAt(filled, c2, N).

% Bindings on transitions 
firesAt(e3, N) :- firesAt(e1, N), enabled(e3, N).

% Time range 
time(0..10).