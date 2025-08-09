<template>
  <div>
    <label>Filter by OS:</label>
    <select @change="onChange" v-model="selected">
      <option value="">All</option>
      <option value="Windows">Windows</option>
      <option value="Darwin">macOS</option>
      <option value="Linux">Linux</option>
    </select>
  </div>
</template>

<script>
export default {
  data() {
    return { selected: "" }
  },
  methods: {
    onChange() {
      this.$emit('filter', this.selected)
    }
  }
}
</script>
