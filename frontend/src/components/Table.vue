<template>
  <div v-if="isWsl" style="margin:8px 0;padding:8px;border:1px solid #ccc;background:#fffbea;font-size:14px;">
    Running inside WSL – some checks are skipped (disk encryption, OS updates, AV, sleep settings).
  </div>
  <table>
    <thead>
      <tr>
        <th>Machine ID</th>
        <th>OS</th>
        <th>Last Check-in</th>
        <th>Disk Encryption</th>
        <th>OS Update</th>
        <th>Antivirus</th>
        <th>Sleep</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="m in machines" :key="m.machine_id">
        <td>{{ m.machine_id }}</td>
        <td>{{ m.os }}</td>
        <td>{{ new Date(m.last_checkin).toLocaleString() }}</td>
        <td>
          <StatusBadge :ok="m.results.disk_encryption.status" :skipped="m.results.disk_encryption.skipped" :reason="m.results.disk_encryption.reason"/>
        </td>
        <td>
          <StatusBadge :ok="m.results.os_update.up_to_date" :skipped="m.results.os_update.skipped" :reason="m.results.os_update.reason"/>
        </td>
        <td>
          <StatusBadge :ok="m.results.antivirus.present && m.results.antivirus.enabled" :skipped="m.results.antivirus.skipped" :reason="m.results.antivirus.reason"/>
        </td>
        <td>
          <StatusBadge :ok="(m.results.inactivity_sleep.sleep_minutes !== null && m.results.inactivity_sleep.sleep_minutes <= 10)" :skipped="m.results.inactivity_sleep.skipped" :reason="m.results.inactivity_sleep.reason"/>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import StatusBadge from './StatusBadge.vue'
export default {
  props: ['machines'],
  components: { StatusBadge },
  computed: {
    isWsl() {
      if (!this.machines || !this.machines.length) return false
      const meta = this.machines[0].results && this.machines[0].results._meta
      return meta && meta.wsl
    }
  }
}
</script>
