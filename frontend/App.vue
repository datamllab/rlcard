<template>
  <div id="app">
    <el-container>
      <el-header>Leaderboard</el-header>
      <el-container>
        <el-aside width="200px">
          <el-row class="tac">
            <el-col>
              <p>Games</p>
              <el-menu
                default-active="1"
                class="el-menu-vertical-demo"
                @open="handleOpen"
                @close="handleClose">
                <el-menu-item index="1">
                  <i class="el-icon-menu"></i>
                  <span>Blackjack</span>
                </el-menu-item>
                <el-menu-item index="2">
                  <i class="el-icon-menu"></i>
                  <span>Doudizhu</span>
                </el-menu-item>
                <el-menu-item index="3">
                  <i class="el-icon-menu"></i>
                  <span>Leduc Hold'em</span>
                </el-menu-item>
                <el-menu-item index="4">
                  <i class="el-icon-menu"></i>
                  <span>Limit Hold'em</span>
                </el-menu-item>
                <el-menu-item index="5">
                  <i class="el-icon-menu"></i>
                  <span>Mahjong</span>
                </el-menu-item>
                <el-menu-item index="6">
                  <i class="el-icon-menu"></i>
                  <span>No-Limit Hold'em</span>
                </el-menu-item>
                <el-menu-item index="7">
                  <i class="el-icon-menu"></i>
                  <span>Uno</span>
                </el-menu-item>
              </el-menu>
            </el-col>
          </el-row>
        </el-aside>
        <el-main>
          <template>
            <el-table
              :data="tableData"
              style="width: 50%"
              stripe='true'>
              <el-table-column
                prop="rank"
                label="Rank">
              </el-table-column>
              <el-table-column
                prop="agent"
                label="Agent">
              </el-table-column>
              <el-table-column
                prop="score"
                label="Score">
              </el-table-column>
            </el-table>
          </template>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
    export default {
      data() {
        return {
          tableData: [{
            rank: '1',
            agent: 'NFSP',
            score: '10,000'
          }, {
            rank: '2',
            agent: 'DQN',
            score: '9,500'
          }, {
            rank: '3',
            agent: 'Deep CFR',
            score: '7,000'
          }, {
            rank: '4',
            agent: 'CFR',
            score: '5,600'
          }]
        }
      }
    }
  </script>

<style>
  @import url("//unpkg.com/element-ui@2.12.0/lib/theme-chalk/index.css");
  .el-header, .el-footer {
    background-color: #B3C0D1;
    color: #333;
    text-align: center;
    line-height: 60px;
  }
  
  .el-aside {
    background-color: #D3DCE6;
    color: #333;
    text-align: center;
    line-height: 20px;
  }
  
  .el-main {
    background-color: #E9EEF3;
    color: #333;
    text-align: center;
    line-height: 20px;
  }
  
  body > .el-container {
    margin-bottom: 40px;
  }
  
  .el-container:nth-child(5) .el-aside,
  .el-container:nth-child(6) .el-aside {
    line-height: 260px;
  }
  
  .el-container:nth-child(7) .el-aside {
    line-height: 320px;
  }
</style>
