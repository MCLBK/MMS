import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Linking,
} from 'react-native';
import {colors, spacing, radius} from '../theme';
import {api} from '../services/api';
import type {DeliveryAssignment} from '../types';

const STATUS_LABELS: Record<string, string> = {
  assigned: 'Assignee',
  courier_accepted: 'Acceptee',
  pickup_in_progress: 'Recup. en cours',
  picked_up: 'Recuperee',
  in_transit: 'En transit',
  arriving: 'Arrivee imminente',
  delivered: 'Livree',
};

const ACTIONS: Record<string, {label: string; next: string; color: string}[]> = {
  assigned: [{label: 'Accepter', next: 'courier_accepted', color: colors.success}],
  courier_accepted: [{label: 'Aller chercher', next: 'pickup_in_progress', color: colors.accent}],
  pickup_in_progress: [{label: 'Colis recupere', next: 'picked_up', color: colors.secondary}],
  picked_up: [{label: 'En route', next: 'in_transit', color: colors.accent}],
  in_transit: [{label: "J'arrive", next: 'arriving', color: colors.warning}],
  arriving: [{label: 'Livre', next: 'delivered', color: colors.success}],
};

interface Props {
  route: {params: {delivery: DeliveryAssignment; companyId: string}};
  navigation: any;
}

export function DeliveryDetailScreen({route, navigation}: Props) {
  const {delivery: initial, companyId} = route.params;
  const [delivery, setDelivery] = useState(initial);
  const [loading, setLoading] = useState(false);

  const handleTransition = async (nextStatus: string) => {
    Alert.alert('Confirmer', `Passer au statut "${STATUS_LABELS[nextStatus] || nextStatus}" ?`, [
      {text: 'Annuler', style: 'cancel'},
      {
        text: 'Confirmer',
        onPress: async () => {
          setLoading(true);
          try {
            await api.post(
              `/companies/${companyId}/orders/${delivery.order_id}/transition`,
              {new_status: nextStatus},
            );
            setDelivery({...delivery, status: nextStatus});
          } catch (err: any) {
            Alert.alert('Erreur', err.message);
          } finally {
            setLoading(false);
          }
        },
      },
    ]);
  };

  const openMaps = (address: string) => {
    const encoded = encodeURIComponent(address);
    Linking.openURL(`https://www.google.com/maps/search/?api=1&query=${encoded}`);
  };

  const actions = ACTIONS[delivery.status] || [];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Text style={styles.backText}>{'<'} Retour</Text>
        </TouchableOpacity>
        <Text style={styles.ref}>{delivery.reference}</Text>
      </View>

      <View style={styles.statusCard}>
        <Text style={styles.statusLabel}>Statut</Text>
        <Text style={styles.statusValue}>
          {STATUS_LABELS[delivery.status] || delivery.status}
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ramassage</Text>
        <TouchableOpacity
          style={styles.addressCard}
          onPress={() => openMaps(delivery.pickup_address)}>
          <View style={[styles.dot, {backgroundColor: colors.success}]} />
          <View style={{flex: 1}}>
            <Text style={styles.addressText}>{delivery.pickup_address}</Text>
            <Text style={styles.mapLink}>Ouvrir dans Maps</Text>
          </View>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Livraison</Text>
        <TouchableOpacity
          style={styles.addressCard}
          onPress={() => openMaps(delivery.delivery_address)}>
          <View style={[styles.dot, {backgroundColor: colors.error}]} />
          <View style={{flex: 1}}>
            <Text style={styles.addressText}>{delivery.delivery_address}</Text>
            <Text style={styles.mapLink}>Ouvrir dans Maps</Text>
          </View>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Client</Text>
        <View style={styles.infoCard}>
          <Text style={styles.infoLabel}>{delivery.customer_name}</Text>
          <TouchableOpacity
            onPress={() => Linking.openURL(`tel:${delivery.customer_phone}`)}>
            <Text style={styles.phoneLink}>{delivery.customer_phone}</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.infoRow}>
        <View style={styles.infoPill}>
          <Text style={styles.infoPillLabel}>Priorite</Text>
          <Text style={styles.infoPillValue}>{delivery.priority.toUpperCase()}</Text>
        </View>
      </View>

      {actions.length > 0 && (
        <View style={styles.actionsSection}>
          {actions.map((action) => (
            <TouchableOpacity
              key={action.next}
              style={[styles.actionButton, {backgroundColor: action.color}]}
              onPress={() => handleTransition(action.next)}
              disabled={loading}>
              {loading ? (
                <ActivityIndicator color={colors.white} />
              ) : (
                <Text style={styles.actionText}>{action.label}</Text>
              )}
            </TouchableOpacity>
          ))}
        </View>
      )}

      {delivery.status === 'delivered' && (
        <View style={styles.doneCard}>
          <Text style={styles.doneEmoji}>{'✓'}</Text>
          <Text style={styles.doneText}>Livraison terminee</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.bg},
  content: {padding: spacing.lg, paddingBottom: 100},
  header: {marginBottom: spacing.xl},
  backBtn: {marginBottom: spacing.sm},
  backText: {fontSize: 15, color: colors.accent, fontWeight: '600'},
  ref: {fontSize: 20, fontWeight: '800', color: colors.primary, fontFamily: 'monospace'},
  statusCard: {
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    padding: spacing.lg,
    marginBottom: spacing.xl,
  },
  statusLabel: {fontSize: 12, color: colors.gray[400], marginBottom: 4},
  statusValue: {fontSize: 20, fontWeight: '800', color: colors.white},
  section: {marginBottom: spacing.xl},
  sectionTitle: {fontSize: 14, fontWeight: '700', color: colors.gray[500], marginBottom: spacing.sm},
  addressCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.md,
    backgroundColor: colors.white,
    borderRadius: radius.md,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.gray[200],
  },
  dot: {width: 10, height: 10, borderRadius: 5, marginTop: 4},
  addressText: {fontSize: 15, fontWeight: '600', color: colors.gray[800]},
  mapLink: {fontSize: 13, color: colors.accent, marginTop: 4},
  infoCard: {
    backgroundColor: colors.white,
    borderRadius: radius.md,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.gray[200],
  },
  infoLabel: {fontSize: 15, fontWeight: '600', color: colors.gray[800]},
  phoneLink: {fontSize: 14, color: colors.accent, marginTop: 4},
  infoRow: {flexDirection: 'row', gap: spacing.md, marginBottom: spacing.xl},
  infoPill: {
    backgroundColor: colors.white,
    borderRadius: radius.md,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderWidth: 1,
    borderColor: colors.gray[200],
  },
  infoPillLabel: {fontSize: 11, color: colors.gray[500]},
  infoPillValue: {fontSize: 14, fontWeight: '700', color: colors.primary},
  actionsSection: {gap: spacing.md, marginBottom: spacing.xl},
  actionButton: {
    borderRadius: radius.md,
    paddingVertical: 18,
    alignItems: 'center',
  },
  actionText: {fontSize: 17, fontWeight: '700', color: colors.white},
  doneCard: {
    backgroundColor: colors.success + '15',
    borderRadius: radius.lg,
    padding: spacing.xxl,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.success + '30',
  },
  doneEmoji: {fontSize: 36, color: colors.success, fontWeight: '800', marginBottom: spacing.sm},
  doneText: {fontSize: 17, fontWeight: '700', color: colors.success},
});
