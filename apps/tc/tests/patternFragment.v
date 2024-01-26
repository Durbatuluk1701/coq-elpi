From elpi.apps Require Import tc.
Elpi Override TC TC.Solver All.
Set TC NameShortPath.
Set TC CompilerWithPatternFragment.

Class Y (A: Type).
Class Z (A: Type).
Class Ex (P : Type -> Type) (A: Type).

Module M4.
Local Instance Inst2 A F: (forall (a : Type) (b c : nat), Y (F a b) -> Y (F a c)) -> Z A. Qed.
Goal Z bool.

  Elpi Override TC TC.Solver None.
    Fail apply _.
  Elpi Override TC TC.Solver All.

  apply _.
  Show Proof.
  Unshelve. assumption. (* we keep a, the first arg of F *)
  Show Proof. Qed.

Local Instance Inst1: Y (bool * bool). Qed.

Goal Z bool.

Elpi Override TC TC.Solver None.
  Succeed apply _. 
Elpi Override TC TC.Solver All.
  apply _.

  Show Proof.
  Unshelve. apply bool.
  Show Proof. Qed.

End M4.

Module M5.
Local Instance Inst1: Y (bool * bool). Qed. 
Local Instance Inst2 A F (R: Type -> Type -> Type):  forall x,
  (forall (a : Type), Y (F a)) -> Ex (R x) A. Qed.
Goal forall (A:Type) x (R: Type -> Type -> Type ->Type), Ex (R x x) A. apply _. Qed.
End M5.

Module M1.
Local Instance Inst1: Y (bool * bool). Qed. 
Local Instance Inst2 A F: (forall (a : Type), Y (F a)) -> Z A. Qed.

Goal forall (A:Type), Z A. apply _. Qed.
End M1.

Module M2.
Local Instance Inst1: Y (bool * bool). Qed. 
Local Instance Inst2 A F: (forall (a: Type), Y (F a)) -> Z A. Qed.
Goal Z bool. apply _. Qed.
End M2.

Module M3.
  Local Instance Inst1: Y (bool * bool). Qed. 
  Local Instance Inst2 A F: (forall (a b c d: Type), Y (F b c d)) -> Z A. Qed.
  Goal Z bool. apply _. Qed.
End M3.

Module withAnd.
  Elpi Accumulate TC.Solver lp:{{
    :before "solve-aux-conclusion"
    solve-aux (goal _ _ TyRaw _ _ as G) GL :- not (var TyRaw),
      if (TyRaw = app [global C|_], coq.TC.class? C) fail (GL = [seal G]).
  }}.
  Module M6.
    Class and (a : Prop) (b : Prop).
    Instance andI {a b : Prop} : a -> b -> and a b. Qed.
    Local Instance Inst2 A F: and (F = fun _ _ => nat)
      (forall (a b c: Type), Y (F a b) -> Y (F b c)) 
      -> Z A. Qed.
    Goal Z bool.
      Elpi Typecheck TC.Solver.
      apply _.
      Unshelve.
      1: { reflexivity. }
    Qed.
  End M6.

  Module M10.
    Class and (a : Prop) (b : Prop).
    Instance andI {a b : Prop} : a -> b -> and a b. Qed.
    Local Instance Inst2 A F: and (F = fun _ _ => nat) (forall (a b c: Type), Y (F a b) -> Y (F c b)) 
      -> Z A. Qed.
    Goal Z bool.
      apply _.
      Unshelve.
      reflexivity.
    Qed.
  End M10.
End withAnd.

Module M7.
Local Instance Inst2 A F: (forall (a b c: Type), Y (F a b) -> Y nat) -> Z A. Qed.
Goal Z bool.
  apply _.
Qed.
End M7.

Module M8.
Local Instance Inst2 A F: (forall (a b c: Type), Y nat -> Y (F a b)) -> Z A. Qed.
Goal Z bool.
  apply _.
Qed.
End M8.

Module M9.
  Local Instance Inst2 A F: (forall (a b c: Type), Y (F a b) -> Y (F b c)) -> Z A. Qed.
  Goal Z bool.
    Elpi Accumulate TC.Solver lp:{{
      :before "same-eta2"
      same-eta C _ VarsRev E :-
        coq.say C E CVars,
        coq.mk-app C {std.rev VarsRev} CVars,
        hd-beta E [] Hd Args, coq.mk-app Hd Args EVars,
        var CVars, var EVars, !,
        CEvars = EVars.
    }}.
    eapply _.
    Unshelve.
    apply nat.
  Qed.
End M9.

Module M1b.
Local Instance Inst2 A F: (forall (a : Type), Y (F a)) -> Ex F A. Qed.

Definition goal := forall (A:Type) (f : Type -> Type), (forall x, Y (f x)) ->
  exists g, Ex g A /\ g nat = g bool.

  Section coq.
    Elpi Override TC TC.Solver None.
    Goal goal. 
    Proof.
      intros ???.
      (* eexists (fun _ => nat). *)
      eexists; constructor.
      apply _.
      Show Proof.
    Abort.
  End coq.

  Section elpi.
    Goal goal. 
    Proof.
      intros ???.
      eexists; constructor.
      apply _.
      reflexivity.
      Unshelve.
      apply nat.
    Qed.
  End elpi.

End M1b.

