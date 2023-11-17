<template>
  <div class="row">
    <div class="col-4">
      <div class="part">
        <scheduler-panel v-bind:waiting-task-list="waitingTaskList"
                         v-bind:running-task="runningTask"
                         v-bind:history-task-list="historyTaskList"
                         v-bind:cron-job-list="cronJobList"
        ></scheduler-panel>
      </div>
    </div>
    <div class="col-8">
      <log-panel v-bind:log-content="logContent" :clearLogContent="clearLogContent"></log-panel>
    </div>
  </div>
</template>

<script>
import SchedulerPanel from "../components/SchedulerPanel.vue";
import LogPanel from "../components/base/LogPanel.vue"
import socketApi from "@/util/socket";

export default {
  name: "AutoController",
  components: {LogPanel, SchedulerPanel},
  data() {
    return {
      logId: '0',
      runningTask: undefined,
      waitingTaskList: [],
      historyTaskList: [],
      cronJobList: [],
      taskList: [],
      logContent: '',
      logWebSocket: undefined,
      TaskWebSocket: undefined,
    }
  },
  created() {
    window.myVue = this
    let that = this
    this.logWebSocket = this.socketApi.initWebSocket("ws://localhost:8071/ws/get_log", this.getResult,
        function () {
          that.logWebSocket.webSocketSendJson({msgType: 'get_log'})
        })

    this.TaskWebSocket = this.socketApi.initWebSocket("ws://localhost:8071/ws/get_task_list", this.getResult,
        function () {
          that.TaskWebSocket.webSocketSendJson({msgType: 'get_task_list'})
        })
  },
  mounted: function () {

  },


  methods: {
    clearLogContent: function () {
      console.log("clear log?")
      this.logContent = ''
    },
    getResult: function (data) {
      let msgType = data['msgType']

      if (msgType === null || msgType === undefined || msgType === "" || msgType.length === 0) {
        return
      }
      if (msgType === 'pong') {
        console.log("pong")
      } else if (msgType === 'taskList') {
        this.getTaskResult(data)
      } else if (msgType === 'log') {
        this.getLogResult(data)
      }
    },
    getTaskResult: function (data) {
      let taskList = data['taskList']
      if (taskList.length === 0) {
        return
      }

      this.taskList = taskList;
      let waitingTaskList = []
      let historyTaskList = []
      let cronJobList = []
      let runningTask = undefined

      this.taskList.forEach(
          t => {
            if (t['task_execute_mode'] === 1) {
              if (t['task_status'] === 2) {
                runningTask = t
              } else if (t['task_status'] === 1) {
                waitingTaskList.push(t)
              } else if (t['task_status'] === 5 || t['task_status'] === 4 || t['task_status'] === 3) {
                historyTaskList.push(t)
              }
            } else if (t['task_execute_mode'] === 2) {
              if (t['task_status'] === 6 || t['task_status'] === 7) {
                cronJobList.push(t)
              }
            }
          }
      )
      this.waitingTaskList = waitingTaskList
      this.historyTaskList = historyTaskList
      this.runningTask = runningTask
      this.cronJobList = cronJobList
      if (this.runningTask === undefined) {
        this.logId = '0'
      } else {
        this.logId = runningTask['task_id']
      }
    },


    getLogResult(data) {
      let log = data['log']
      if (log.length === 0) {
        return
      }
      for (let i = 0; i < log.length; i++) {
        this.logContent += (log[i] + '\n');
      }

    },


  }


}
</script>

<style scoped>

</style>