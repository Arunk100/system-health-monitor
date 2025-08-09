<template>
  <div id="app">
    <h1>System Health Monitor</h1>
    <Filters @filter="setFilter"/>
    <div style="margin:8px 0; display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
      <label>Sort by:
        <select v-model="sortKey">
          <option value="last_checkin">Last Check-in</option>
          <option value="machine_id">Machine ID</option>
          <option value="os">OS</option>
        </select>
      </label>
      <label>Direction:
        <select v-model="sortDir">
          <option value="desc">Desc</option>
          <option value="asc">Asc</option>
        </select>
      </label>
      <label>
        <input type="checkbox" v-model="onlyIssues"/> Only issues
      </label>
      <button @click="manualRefresh">Refresh</button>
      <a :href="csvUrl" target="_blank">Download CSV</a>
      <small v-if="autoRef" style="opacity:0.6">Auto-refresh 30s</small>
    </div>
    <Table :machines="displayed"/>
  </div>
</template>

<script>
import Table from './components/Table.vue'
import Filters from './components/Filters.vue'
import { fetchMachines } from './api'

export default {
  name: 'App',
  components: { Table, Filters },
  data() {
    return {
      machines: [],
      filter: null,
      sortKey: 'last_checkin',
      sortDir: 'desc',
      onlyIssues: false,
      autoRef: true,
      timer: null,
    }
  },
  computed: {
    filtered() {
      let arr = this.machines.slice()
      if (this.filter) arr = arr.filter(m => m.os === this.filter)
      if (this.onlyIssues) arr = arr.filter(m => this.isIssue(m))
      return arr
    },
    sorted() {
      const arr = this.filtered.slice()
      const k = this.sortKey
      arr.sort((a,b) => {
        let av = a[k]; let bv = b[k]
        if (k === 'last_checkin') { av = new Date(av).getTime(); bv = new Date(bv).getTime() }
        if (av < bv) return this.sortDir === 'asc' ? -1 : 1
        if (av > bv) return this.sortDir === 'asc' ? 1 : -1
        return 0
      })
      return arr
    },
    displayed() { return this.sorted },
    csvUrl() {
      const params = new URLSearchParams()
      if (this.filter) params.set('os', this.filter)
      if (this.onlyIssues) params.set('issues','true')
      return 'http://localhost:8000/machines.csv' + (params.toString() ? ('?' + params.toString()) : '')
    }
  },
  methods: {
    setFilter(os) { this.filter = os },
    async load() { this.machines = await fetchMachines(this.onlyIssues) },
    isIssue(m) {
      const r = m.results || {}
      try { const de = r.disk_encryption; if (de && !de.skipped && de.status === false) return true } catch(_){}
      try { const ou = r.os_update; if (ou && !ou.skipped && ou.up_to_date === false) return true } catch(_){}
      try { const av = r.antivirus; if (av && !av.skipped && (av.present === false || av.enabled === false)) return true } catch(_){}
      try { const sl = r.inactivity_sleep; if (sl && !sl.skipped && sl.sleep_minutes != null && sl.sleep_minutes > 10) return true } catch(_){}
      return false
    },
    async manualRefresh() { await this.load() }
  },
  async mounted() {
    await this.load()
    if (this.autoRef) this.timer = setInterval(this.load, 30000)
  },
  beforeUnmount() { if (this.timer) clearInterval(this.timer) }
}
</script>
