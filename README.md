# Pathfinding algorithms

## Description

This application lets you create your own labyrinth and then observe how different pathfinding algorithms work to find the optimal way between two points in your map. 
It is entirely written in Python in order to use Tkinter for the graphical interface as it cas the first purpose of the college project.  
It was a part of a college project that I pushed a little too far but it was really interesting to code and to discover new algorithms.

## How to use

* Clone the project locally
* Run the main
* You can use the existing map or create your own by clicking on the "Change map" button
  * If you choose to change the map, you can choose the number of rows and columns at the bottom of the screen with the scroller or the textbox
  * Add walls by leftclicking on the tiles (or maintaining leftclick and dragging)
  * Remove walls by rightclicking on existing walls (or maintaining rightclick and dragging)
  * Reset the map by clicking on the "Clear map" button
  * Confirm your map with the "Confirm" button, your map is saved in maps/map.txt
* Choose the algorithm you want to use at the bottom left of the window
* Choose a start point by clicking on an available tile (not a wall)
* Then choose an end point the same way
* You can see the time execution at the bottom of the window and an animation of the tiles that are used by the algorithm (green for the open_list, blue for the close_list)
* The buttons are disabled when the animation is on, and when finished you can start again with the "Restart" button

## Sources

The Dijkstra and A* come from my college courses.  
I found the JPS by my own by reading a research paper that was really interesting and useful :  
http://grastien.net/ban/articles/hg-aaai11.pdf

Then I find an even better version of the JPS called the JPS+ :  
https://www.gameaipro.com/GameAIPro2/GameAIPro2_Chapter14_JPS_Plus_An_Extreme_A_Star_Speed_Optimization_for_Static_Uniform_Cost_Grids.pdf


