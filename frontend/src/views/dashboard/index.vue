<template>
  <div class="dashboard-container">
    <div style="text-align: center; padding-top: 15%;">
      <el-image
        :src="logo"
      />
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Dashboard',
  data() {
    return {
      // url: require('/src/assets/img/nasa_l.jpg'),
      logo: require('/src/assets/img/logo.png')
    }
  },
  computed: {
    ...mapGetters([
      'name'
    ])
  }
}
</script>

<style lang="scss" scoped>
.dashboard-container {
  height:100%;
  width:100%;
  position:fixed;
  background-image: url("../../assets/img/nasa_l.jpg");
}
</style>
