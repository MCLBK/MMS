import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import {colors, spacing, radius} from '../theme';
import {useAuthStore} from '../store/auth';

export function HomeScreen() {
  const user = useAuthStore((s) => s.user);

  const stats = [
    {label: "Aujourd'hui", value: '—', color: colors.accent},
    {label: 'En cours', value: '—', color: colors.warning},
    {label: 'Terminees', value: '—', color: colors.success},
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Bonjour,</Text>
          <Text style={styles.name}>
            {user?.first_name} {user?.last_name}
          </Text>
        </View>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user?.first_name?.[0]}
            {user?.last_name?.[0]}
          </Text>
        </View>
      </View>

      <View style={styles.statsRow}>
        {stats.map((s) => (
          <View key={s.label} style={styles.statCard}>
            <Text style={[styles.statValue, {color: s.color}]}>{s.value}</Text>
            <Text style={styles.statLabel}>{s.label}</Text>
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Livraisons assignees</Text>
        <View style={styles.emptyCard}>
          <Text style={styles.emptyIcon}>📦</Text>
          <Text style={styles.emptyText}>Aucune livraison en attente</Text>
          <Text style={styles.emptySubtext}>
            Les nouvelles livraisons apparaitront ici
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Actions rapides</Text>
        <View style={styles.actionsGrid}>
          {[
            {title: 'Disponibilite', emoji: '🟢'},
            {title: 'Historique', emoji: '📋'},
            {title: 'Ma position', emoji: '📍'},
            {title: 'Parametres', emoji: '⚙️'},
          ].map((action) => (
            <TouchableOpacity key={action.title} style={styles.actionCard}>
              <Text style={styles.actionEmoji}>{action.emoji}</Text>
              <Text style={styles.actionTitle}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  content: {
    padding: spacing.lg,
    paddingBottom: 100,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  greeting: {
    fontSize: 14,
    color: colors.gray[500],
  },
  name: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.primary,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.accent + '20',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.accent,
  },
  statsRow: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.xl,
  },
  statCard: {
    flex: 1,
    backgroundColor: colors.white,
    borderRadius: radius.md,
    padding: spacing.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.gray[200],
  },
  statValue: {
    fontSize: 28,
    fontWeight: '800',
  },
  statLabel: {
    fontSize: 12,
    color: colors.gray[500],
    marginTop: 4,
  },
  section: {
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: spacing.md,
  },
  emptyCard: {
    backgroundColor: colors.white,
    borderRadius: radius.lg,
    padding: spacing.xxl,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.gray[200],
  },
  emptyIcon: {
    fontSize: 40,
    marginBottom: spacing.md,
  },
  emptyText: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.gray[600],
  },
  emptySubtext: {
    fontSize: 13,
    color: colors.gray[400],
    marginTop: 4,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  actionCard: {
    width: '47%',
    backgroundColor: colors.white,
    borderRadius: radius.md,
    padding: spacing.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.gray[200],
  },
  actionEmoji: {
    fontSize: 28,
    marginBottom: spacing.sm,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.gray[700],
  },
});
