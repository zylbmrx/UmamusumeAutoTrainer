<template>
  <div>
    <div class="card">
      <div class="card-body">
        <div class="d-flex bd-highlight mb-3">
          <h5 class="card-title">日志</h5>
          <div class="ml-auto btn-group" role="group" aria-label="Basic example">
            <span>
              <button class="ml-auto btn auto-btn" v-on:click="clearLog">清空日志</button>
            </span>
            <span>&nbsp;</span>
            <span>
            <button v-on:click="autoScroll = !autoScroll" class="ml-auto btn auto-btn">
              <span v-if="autoScroll"><font-awesome-icon icon="fa-regular fa-circle-play"/> 自动滚动：开</span>
              <span v-if="!autoScroll"><font-awesome-icon icon="fa-regular fa-circle-pause"/> 自动滚动：关</span>
            </button>
            </span>
          </div>


        </div>
        <div>
          <div class="input-group">
            <textarea id="scroll_text" disabled v-bind:placeholder="logContent" class="form-control"
                      aria-label="With textarea">{{logContent}}</textarea>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LogPanel",
  props: {
    logContent: {
      type: String,
      default: ''
    }
    , clearLogContent: {
      type: Function,
      default: null
    }
  },
  methods: {
    clearLog: function () {
      this.clearLogContent()
    },

  },
  data: function () {
    return {
      autoScroll: true,
    }
  },
  updated: function () {
    if (this.autoScroll) {
      const textarea = document.getElementById('scroll_text');
      textarea.scrollTop = textarea.scrollHeight;
    }
  }
}
</script>

<style scoped>
textarea {
  min-height: 600px;
  font-size: 12px;
}

.form-control:disabled {
  background: #fff;
}
</style>