<template>
  <div id="app">
    <el-container style="height: 750px;">
      <el-header>
        <h1>
          <font face='Arial'>
            RLCard Leaderboard
          </font>
        </h1>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-row class="tac">
            <el-col>
              <h2 align='center'>
                <span>
                    <font 
                      face='Arial'
                      size='5'>  
                      Games
                    </font>  
                  </span>
              </h2>
              <el-menu
                default-active="1"
                class="el-menu-vertical"
                @open="handleOpen"
                @close="handleClose"
                background-color=#E9EEF3>
                <el-menu-item index="1">
                  <i class="el-icon-menu"></i>
                  <span>
                    <font 
                      face='Arial'
                      color=#333>  
                      Blackjack
                    </font>  
                  </span>
                </el-menu-item>
                <el-menu-item index="2">
                  <i class="el-icon-menu"></i>
                  <span>
                    <font 
                      face='Arial'
                      color=#333>  
                      Doudizhu
                    </font>  
                  </span>
                </el-menu-item>
                <el-menu-item index="3">
                  <i class="el-icon-menu"></i>
                  <span>
                    <font 
                      face='Arial'
                      color=#333>
                      Leduc Hold'em
                    </font>  
                  </span>
                </el-menu-item>
                <el-menu-item index="4">
                  <i class="el-icon-menu"></i>
                  <span>
                    <font 
                      face='Arial'
                      color=#333> 
                      Limit Hold'em
                    </font>  
                  </span>
                </el-menu-item>
                <el-menu-item index="5">
                  <i class="el-icon-menu"></i>
                  <span>
                    <font 
                      face='Arial'
                      color=#333>
                      Mahjong
                    </font>  
                  </span>
                </el-menu-item>
                <el-menu-item index="6">
                  <i class="el-icon-menu"></i>
                  <span>
                    <font 
                      face='Arial'
                      color=#333> 
                      No-Limit Hold'em
                    </font>  
                  </span>
                </el-menu-item>
                <el-menu-item index="7">
                  <i class="el-icon-menu"></i>
                  <span>
                    <font 
                      face='Arial'
                      color=#333>
                      Uno
                    </font>  
                  </span>
                </el-menu-item>
              </el-menu>
            </el-col>
          </el-row>
        </el-aside>
        <el-main>
          <div align='center'>
            <el-table
              :data="tableData"
              style="width: 50%"
              stripe="true">
              <el-table-column
                prop="rank"
                label="Rank"
                align='center'>
              </el-table-column>
              <el-table-column
                prop="agent"
                label="Agent"
                align='center'>
              </el-table-column>
              <el-table-column
                prop="score"
                label="Score"
                align='center'>
              </el-table-column>
            </el-table>
          </div>
        </el-main>
      </el-container>
      <el-container>
        <el-footer>
          <h2>
            <font face='Arial'>
              DATA Lab
            </font>
          </h2>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script>
    export default {
      data() {
        return {
          tableData: []
        }
      },
      mounted() {
        this.axios.get("http://www.mocky.io/v2/5dc10315330000f22d1a4dad") 
                  .then(response=>{ 
                    this.tableData = response.data;
                  }) 
      }
    }
  </script>

<style>
  .el-header, .el-footer {
    background-color: #B3C0D1;
    color: #333;
    text-align: center;
  }
  
  .el-aside {
    background-color: #D3DCE6;
    color: #333;
    text-align: left;
  }
  
  .el-main {
    background-color: #E9EEF3;
    color: #333;
    text-align: center;
  }

  h1 {
    font-size: 2em;
    margin-top: 0.35em;
    font-weight: 500;
  }
  
  h2 {
    font-size: 1.1em;
    margin-top: 1.2em;
    font-weight: 500;
  }
  
</style>