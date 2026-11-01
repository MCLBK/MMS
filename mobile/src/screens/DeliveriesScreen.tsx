import React, {useEffect, useState, useCallback} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import {colors, spacing, radius} from '../theme';
import {api} from '../services/api';
import type {DeliveryAssignment} from '../types';

const COMPANY_ID = '00000000-0000-0000-0000-000000000001';

const STATUS_COLORS: Record<string, {bg: string; text: string}> = {
  assigned: {bg: colors.accent + '20', text: colors.accent},
  courier_accepted: {bg: colors.secondary + '20', text: colors.secondary},
  pickup_in_progress: {bg: colors.warning + '20', text: colors.warning},
  picked_up: {bg: colors.secondary + '20', text: colors.secondary},
  in_transit: {bg: colors.accent + '20', text: colors.accent},
  arriving: {bg: colors.warning + '20', text: colors.warning},
  delivered: {bg: colors.success + '20', text: colors.success},
};

const STATUS_LABELS: Record<string, string> = {
  assigned: 'Assignee',
  courier_accepted: 'Acceptee',
  pickup_in_progress: 'Recup. en cours',
  picked_up: 'Recuperee',
  in_transit: 'En transit',
  arriving: 'Arrivee imminente',
  delivered: 'Livree',
};

function DeliveryCard({
  item,
  onPress,
}: {
  item: DeliveryAssignment;
  onPress: () => void;
}) {
  const statusStyle = STATUS_COLORS[item.status] || {
    bg: colors.gray[200],
    text: colors.gray[600],
  };

  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <View style={styles.cardHeader}>
        <Text style={styles.reference}>{item.reference}</Text>
        <View style={[styles.statusBadge, {backgroundColor: statusStyle.bg}]}>
          <Text style={[styles.statusText, {color: statusStyle.text}]}>
            {STATUS_LABELS[item.status] || item.status}
          </Text>
        </View>
      </View>
      <View style={styles.addressRow}>
        <View style={[styles.dot, {backgroundColor: colors.success}]} />
        <Text style={styles.addressText} numberOfLines={1}>
          {item.pickup_address}
        </Text>
      </View>
      <View style={styles.addressRow}>
        <View style={[styles.dot, {backgroundColor: colors.error}]} />
        <Text style={styles.addressText} numberOfLines={1}>
          {item.delivery_address}
        </Text>
      </View>
      <View style={styles.cardFooter}>
        <Text style={styles.customerName}>{item.customer_name}</Text>
        <Text style={styles.priority}>{item.priority}</Text>
      </View>
    </TouchableOpacity>
  );
}

export function DeliveriesScreen({navigation}: {navigation: any}) {
  const [deliveries, setDeliveries] = useState<DeliveryAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDeliveries = useCallback(async () => {
    try {
      const data = await api.get<DeliveryAssignment[]>(
        `/companies/${COMPANY_ID}/couriers/my-deliveries`,
      );
      setDeliveries(data);
    } catch {
      setDeliveries([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDeliveries();
  }, [fetchDeliveries]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchDeliveries();
  }, [fetchDeliveries]);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.accent} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={deliveries}
        keyExtractor={(item) => item.id}
        renderItem={({item}) => (
          <DeliveryCard
            item={item}
            onPress={() =>
              navigation.navigate('DeliveryDetail', {
                delivery: item,
                companyId: COMPANY_ID,
              })
            }
          />
        )}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[colors.accent]}
          />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>{'📦'}</Text>
            <Text style={styles.emptyTitle}>Aucune livraison</Text>
            <Text style={styles.emptySubtext}>
              Vos livraisons assignees apparaitront ici
            </Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.bg},
  loadingContainer: {flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.bg},
  list: {padding: spacing.lg, paddingBottom: 100, gap: spacing.md},
  card: {
    backgroundColor: colors.white,
    borderRadius: radius.md,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.gray[200],
    gap: spacing.sm,
  },
  cardHeader: {flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center'},
  reference: {fontSize: 13, fontWeight: '700', color: colors.primary, fontFamily: 'monospace'},
  statusBadge: {paddingHorizontal: 10, paddingVertical: 4, borderRadius: radius.sm},
  statusText: {fontSize: 12, fontWeight: '600'},
  addressRow: {flexDirection: 'row', alignItems: 'center', gap: spacing.sm},
  dot: {width: 8, height: 8, borderRadius: 4},
  addressText: {fontSize: 14, color: colors.gray[600], flex: 1},
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.gray[100],
  },
  customerName: {fontSize: 13, fontWeight: '600', color: colors.gray[700]},
  priority: {fontSize: 12, color: colors.gray[500], textTransform: 'uppercase'},
  empty: {alignItems: 'center', paddingVertical: 60},
  emptyIcon: {fontSize: 48, marginBottom: spacing.md},
  emptyTitle: {fontSize: 17, fontWeight: '700', color: colors.gray[600]},
  emptySubtext: {fontSize: 14, color: colors.gray[400], marginTop: 4},
});
