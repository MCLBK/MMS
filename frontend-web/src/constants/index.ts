export const ORDER_STATUS_LABELS: Record<string, string> = {
  draft: "Brouillon",
  pending: "En attente",
  analyzing: "Analyse en cours",
  ready_to_assign: "Pret a attribuer",
  assigning: "Attribution en cours",
  assigned: "Attribue",
  courier_accepted: "Accepte par le livreur",
  pickup_in_progress: "Enlevement en cours",
  picked_up: "Enleve",
  in_transit: "En transit",
  arriving: "Arrivee imminente",
  delivered: "Livre",
  confirmed: "Confirme",
  completed: "Termine",
  courier_refused: "Refuse par le livreur",
  expired: "Expire",
  delivery_failed: "Echec de livraison",
  cancelled: "Annule",
  disputed: "Conteste",
  under_review: "En revision",
  resolved: "Resolu",
};

export const ORDER_STATUS_VARIANTS: Record<string, string> = {
  draft: "default",
  pending: "warning",
  analyzing: "secondary",
  ready_to_assign: "accent",
  assigning: "accent",
  assigned: "accent",
  courier_accepted: "success",
  pickup_in_progress: "accent",
  picked_up: "accent",
  in_transit: "accent",
  arriving: "accent",
  delivered: "success",
  confirmed: "success",
  completed: "success",
  courier_refused: "error",
  expired: "error",
  delivery_failed: "error",
  cancelled: "default",
  disputed: "warning",
  under_review: "warning",
  resolved: "success",
};

export const PRIORITY_LABELS: Record<string, string> = {
  low: "Faible",
  normal: "Normale",
  high: "Haute",
  urgent: "Urgente",
};

export const PRIORITY_VARIANTS: Record<string, string> = {
  low: "default",
  normal: "secondary",
  high: "warning",
  urgent: "error",
};

export const VEHICLE_TYPE_LABELS: Record<string, string> = {
  bicycle: "Velo",
  motorcycle: "Moto",
  car: "Voiture",
  van: "Camionnette",
  truck: "Camion",
};

export const COURIER_STATUS_LABELS: Record<string, string> = {
  available: "Disponible",
  busy: "Occupe",
  offline: "Hors ligne",
};

export const COURIER_STATUS_VARIANTS: Record<string, string> = {
  available: "success",
  busy: "warning",
  offline: "default",
};
