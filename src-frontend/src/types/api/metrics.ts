import { z } from 'zod';
import {
  DoorUniqueMembersDailySchema,
  MemberbucksBalanceTotalSchema,
  MemberbucksTransactionsTotalSchema,
  MemberCountTotalSchema,
  OnSiteMetricsSchema,
  SubscriptionCountTotalSchema,
} from 'types/metrics';

export const MetricsApiSchema = z.object({
  on_site: OnSiteMetricsSchema,
  member_count_total: z.array(MemberCountTotalSchema),
  member_count_6_months_total: z.array(MemberCountTotalSchema),
  member_count_12_months_total: z.array(MemberCountTotalSchema),
  subscription_count_total: z.array(SubscriptionCountTotalSchema),
  memberbucks_balance_total: z.array(MemberbucksBalanceTotalSchema),
  memberbucks_transactions_total: z.array(MemberbucksTransactionsTotalSchema),
  door_unique_members_daily: z.array(DoorUniqueMembersDailySchema),
});

export type MetricsApi = z.infer<typeof MetricsApiSchema>;
