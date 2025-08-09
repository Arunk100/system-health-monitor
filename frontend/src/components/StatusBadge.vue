<template>
  <span :style="styleObj" :title="tooltip">{{ label }}</span>
</template>

<script>
export default {
  props: {
    ok: { type: Boolean, required: false },
    skipped: { type: Boolean, required: false, default: false },
    reason: { type: String, required: false }
  },
  computed: {
    label() {
      if (this.skipped) return 'Skipped'
      if (this.ok === undefined || this.ok === null) return 'Unknown'
      return this.ok ? 'OK' : 'Issue'
    },
    styleObj() {
      if (this.skipped) return { color: '#888' }
      if (this.ok) return { color: 'green' }
      return { color: 'red' }
    },
    tooltip() {
      if (this.skipped) return this.reason || 'Check skipped'
      if (this.ok === false) return 'Issue detected'
      if (this.ok === true) return 'OK'
      return 'Unknown'
    }
  }
}
</script>
