<template>
  <div class="flex flex-col h-full overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: __('Lead History'), route: { name: 'LeadHistory' } }]" />
      </template>
      <template #right-header>
        <Link
          v-if="isAdmin() || isManager()"
          class="form-control w-56"
          variant="outline"
          :value="selectedUser && getUser(selectedUser)?.full_name"
          doctype="User"
          @change="onUserChange"
          :placeholder="__('Select user')"
          :hideMe="true"
        >
          <template #prefix>
            <UserAvatar
              v-if="selectedUser"
              class="mr-2"
              :user="selectedUser"
              size="sm"
            />
          </template>
          <template #item-prefix="{ option }">
            <UserAvatar class="mr-2" :user="option.value" size="sm" />
          </template>
          <template #item-label="{ option }">
            <Tooltip :text="option.value">
              <div class="cursor-pointer">
                {{ getUser(option.value).full_name }}
              </div>
            </Tooltip>
          </template>
        </Link>
        <Button
          :label="__('Refresh')"
          :iconLeft="LucideRefreshCcw"
          @click="loadHistory"
        />
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto p-5">
      <!-- Loading state -->
      <div v-if="loading" class="flex h-full items-center justify-center">
        <div class="text-base text-ink-gray-4">{{ __('Loading lead history...') }}</div>
      </div>

      <div v-else>
        <!-- Stats cards - Global view -->
        <div v-if="viewType === 'global'" class="grid grid-cols-3 gap-4 mb-6">
          <div class="rounded-lg border bg-surface-gray-2 p-4 text-center">
            <div class="text-sm text-ink-gray-5 mb-1">{{ __('Completed') }}</div>
            <div class="text-2xl font-bold text-ink-green-3">{{ doneCount }}</div>
          </div>
          <div class="rounded-lg border bg-surface-gray-2 p-4 text-center">
            <div class="text-sm text-ink-gray-5 mb-1">{{ __('Rejected') }}</div>
            <div class="text-2xl font-bold text-ink-red-3">{{ rejectedCount }}</div>
          </div>
          <div class="rounded-lg border bg-surface-gray-2 p-4 text-center">
            <div class="text-sm text-ink-gray-5 mb-1">{{ __('Total') }}</div>
            <div class="text-2xl font-bold text-ink-gray-9">{{ leads.length }}</div>
          </div>
        </div>

        <!-- Stats cards - Personal view -->
        <div v-else class="grid grid-cols-1 gap-4 mb-6" style="max-width: 250px;">
          <div class="rounded-lg border bg-surface-gray-2 p-4 text-center">
            <div class="text-sm text-ink-gray-5 mb-1">{{ __('Total Leads Handled') }}</div>
            <div class="text-2xl font-bold text-ink-blue-3">{{ leads.length }}</div>
          </div>
        </div>

        <!-- Viewing indicator -->
        <div
          v-if="historyData?.full_name && selectedUser"
          class="mb-4 flex items-center gap-2 rounded-lg border border-outline-gray-2 bg-surface-gray-2 px-4 py-2"
        >
          <UserAvatar :user="selectedUser" size="sm" />
          <span class="text-sm text-ink-gray-7">
            {{ __('Viewing history for') }}
            <span class="font-semibold text-ink-gray-9">{{ historyData.full_name }}</span>
          </span>
        </div>

        <!-- Filters row -->
        <div class="mb-4 flex items-center gap-3 flex-wrap">
          <div class="flex items-center gap-2">
            <label class="text-xs font-semibold text-ink-gray-5 uppercase">{{ __('Status') }}</label>
            <select
              v-model="filterStatus"
              class="form-control text-sm"
              style="width: 150px; height: 30px; padding: 2px 8px;"
            >
              <option value="">{{ __('All') }}</option>
              <option value="Working">{{ __('Working') }}</option>
              <option value="Done">{{ __('Done') }}</option>
              <option value="Rejected">{{ __('Rejected') }}</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <label class="text-xs font-semibold text-ink-gray-5 uppercase">{{ __('Action') }}</label>
            <select
              v-model="filterAction"
              class="form-control text-sm"
              style="width: 180px; height: 30px; padding: 2px 8px;"
            >
              <option value="">{{ __('All') }}</option>
              <option value="Forward">{{ __('Mark Done') }}</option>
              <option value="Backward">{{ __('Send Back') }}</option>
              <option value="Reject">{{ __('Reject') }}</option>
              <option value="Manager Override">{{ __('Transfer') }}</option>
              <option value="Initial">{{ __('Initial') }}</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <label class="text-xs font-semibold text-ink-gray-5 uppercase">{{ __('Search') }}</label>
            <input
              v-model="searchQuery"
              type="text"
              class="form-control text-sm"
              :placeholder="__('Lead name or ID...')"
              style="width: 200px; height: 30px; padding: 2px 8px;"
            />
          </div>
          <Button
            v-if="filterStatus || filterAction || searchQuery"
            :label="__('Clear')"
            variant="subtle"
            theme="gray"
            size="sm"
            @click="clearFilters"
          />
        </div>

        <!-- Previously Handled Leads table -->
        <div>
          <h3 class="text-base font-semibold text-ink-gray-9 mb-3 flex items-center gap-2">
            <span>✅</span>
            {{ viewType === 'global' ? __('All Completed / Rejected Leads') : __('Previously Handled Leads') }}
            <span class="text-sm font-normal text-ink-gray-5">({{ filteredLeads.length }})</span>
          </h3>
          <div v-if="filteredLeads.length" class="rounded-lg border overflow-hidden">
            <table class="w-full">
              <thead>
                <tr class="bg-surface-gray-2">
                  <th class="px-4 py-2.5 text-left text-xs font-semibold text-ink-gray-5 uppercase tracking-wide">{{ __('Lead ID') }}</th>
                  <th class="px-4 py-2.5 text-left text-xs font-semibold text-ink-gray-5 uppercase tracking-wide">{{ __('Name') }}</th>
                  <th class="px-4 py-2.5 text-left text-xs font-semibold text-ink-gray-5 uppercase tracking-wide">{{ __('Current Department') }}</th>
                  <th class="px-4 py-2.5 text-left text-xs font-semibold text-ink-gray-5 uppercase tracking-wide">{{ viewType === 'global' ? __('Last Action') : __('Action Taken') }}</th>
                  <th class="px-4 py-2.5 text-left text-xs font-semibold text-ink-gray-5 uppercase tracking-wide">{{ __('Status') }}</th>
                  <th v-if="viewType === 'global'" class="px-4 py-2.5 text-left text-xs font-semibold text-ink-gray-5 uppercase tracking-wide">{{ __('Last Handled By') }}</th>
                  <th class="px-4 py-2.5 text-left text-xs font-semibold text-ink-gray-5 uppercase tracking-wide">{{ __('Last Updated') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="lead in filteredLeads"
                  :key="lead.name"
                  class="border-t border-outline-gray-2 hover:bg-surface-gray-2 cursor-pointer transition-colors"
                  @click="openLead(lead.name)"
                >
                  <td class="px-4 py-2.5">
                    <span class="text-sm font-medium text-ink-blue-3 hover:underline">{{ lead.name }}</span>
                  </td>
                  <td class="px-4 py-2.5 text-sm text-ink-gray-8">{{ lead.lead_name || '-' }}</td>
                  <td class="px-4 py-2.5">
                    <Badge variant="subtle" :label="lead.current_department || '-'" theme="blue" />
                  </td>
                  <td class="px-4 py-2.5">
                    <Badge
                      v-if="getLeadAction(lead)"
                      variant="subtle"
                      :label="getActionLabel(getLeadAction(lead))"
                      :theme="getActionTheme(getLeadAction(lead))"
                    />
                    <span v-else class="text-sm text-ink-gray-5">—</span>
                  </td>
                  <td class="px-4 py-2.5">
                    <Badge
                      variant="subtle"
                      :label="lead.department_status || '-'"
                      :theme="getStatusTheme(lead.department_status)"
                    />
                  </td>
                  <td v-if="viewType === 'global'" class="px-4 py-2.5 text-sm text-ink-gray-7">
                    {{ lead.last_handled_by_name || '—' }}
                  </td>
                  <td class="px-4 py-2.5 text-sm text-ink-gray-6">
                    <Tooltip :text="formatDate(lead.modified)">
                      {{ __(timeAgo(lead.modified)) }}
                    </Tooltip>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="flex items-center justify-center rounded-lg border border-dashed py-8">
            <span class="text-sm text-ink-gray-4">
              {{ (filterStatus || filterAction || searchQuery) ? __('No leads match the selected filters') : (viewType === 'global' ? __('No completed or rejected leads yet') : __('No lead history found')) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LucideRefreshCcw from '~icons/lucide/refresh-ccw'
import LayoutHeader from '@/components/LayoutHeader.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/users'
import { timeAgo, formatDate } from '@/utils'
import { Breadcrumbs, Badge, Tooltip, Button, usePageMeta, call } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { getUser, isManager, isAdmin } = usersStore()

const loading = ref(false)
const selectedUser = ref(null)
const historyData = ref(null)
const leads = ref([])
const viewType = ref('global')
const doneCount = ref(0)
const rejectedCount = ref(0)

// Filters
const filterStatus = ref('')
const filterAction = ref('')
const searchQuery = ref('')

const filteredLeads = computed(() => {
  let result = leads.value
  if (filterStatus.value) {
    result = result.filter(l => l.department_status === filterStatus.value)
  }
  if (filterAction.value) {
    result = result.filter(l => {
      const action = l.last_action || l.user_action
      return action === filterAction.value
    })
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(l =>
      (l.name && l.name.toLowerCase().includes(q)) ||
      (l.lead_name && l.lead_name.toLowerCase().includes(q))
    )
  }
  return result
})

function clearFilters() {
  filterStatus.value = ''
  filterAction.value = ''
  searchQuery.value = ''
}

async function loadHistory() {
  loading.value = true
  try {
    const args = {}
    if (selectedUser.value) {
      args.user = selectedUser.value
    }
    const data = await call(
      'lead_routing.api.lead_history.get_my_lead_history',
      args,
    )
    historyData.value = data
    leads.value = data.leads || []
    viewType.value = data.view_type || 'global'
    doneCount.value = data.done_count || 0
    rejectedCount.value = data.rejected_count || 0
  } catch (e) {
    console.error('Failed to load lead history:', e)
    leads.value = []
  } finally {
    loading.value = false
  }
}

function onUserChange(value) {
  selectedUser.value = value
  clearFilters()
  loadHistory()
}

function openLead(leadId) {
  router.push({ name: 'Lead', params: { leadId } })
}

function getLeadAction(lead) {
  return lead.last_action || lead.user_action || null
}

const actionLabels = {
  'Forward': 'Mark Done',
  'Backward': 'Send Back',
  'Reject': 'Reject to Onboarding',
  'Manager Override': 'Manager Override',
  'Initial': 'Initial Assignment',
}

function getActionLabel(action) {
  return actionLabels[action] || action
}

function getActionTheme(action) {
  const themes = {
    'Forward': 'green',
    'Backward': 'orange',
    'Reject': 'red',
    'Manager Override': 'blue',
    'Initial': 'gray',
  }
  return themes[action] || 'gray'
}

function getStatusTheme(status) {
  if (!status) return 'gray'
  const s = status.toLowerCase()
  if (s === 'done') return 'green'
  if (s === 'rejected') return 'red'
  if (s === 'working') return 'orange'
  return 'blue'
}

onMounted(() => {
  loadHistory()
})

usePageMeta(() => {
  if (viewType.value === 'global' && !selectedUser.value) {
    return { title: __('Lead History — All Completed / Rejected') }
  }
  if (historyData.value?.full_name) {
    return { title: __('Lead History: {0}', [historyData.value.full_name]) }
  }
  return { title: __('Lead History') }
})
</script>
