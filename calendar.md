---
title: "Calendar"
layout: default
navigation_weight: 3
---

## Day 0 / Week 1
no class


## Day 1 / Week 2
Readings/Announcements

* Chapter 3.1 (https://www.nap.edu/read/11793/chapter/5)
* How to find Swem 215 aka the CGA Classroom


[Ice Breaker Challenge](https://drdavis.space/teaching/gis/ice-breaker/)

* work in two teams to deliver spatially significant solutions


## Day 2 / Week 3
Start class with brief video (choose one):

- [Landslides \| National Geographic]( https://youtu.be/mknStAMia0Q)
- [When Nature Strikes - Landslides](https://youtu.be/dj44dpr8oHs?t=18)
- [Mount St. Helens Disintegrates in Enormous Landslide](https://youtu.be/UK--hvgP2uY)

Pop-up consultant firm & website challenge

> In this first scenario, you work for an organization that has tasked you, the GIS experts, to sort out landslide susceptibility for several international clients.
>
> As an organization, we will break into teams (undergrads in teams of 2--3 and graduates/certificate students as individuals or pairs) and will be assigned international clients (chosen at random). Your team will create its own consultant firm (with a name, slogan, logo, etc.) and have a web presence (using GitHub Pages) to communicate your tasks and accomplishments to your clients.
>
> This week, your goals are to:
>
> * form teams
> * create your consultant firm
> * build a web page (blog-style); be sure to include relevant information, such as your firm's name, logo, mission statement, member names, contact, the works
> * determine what might be the motivating reasons for landslide susceptibility analysis for your clients (sometimes you need to tell people what they should be interested in); it may be national security, public health, insurance rates, taxation, etc. (your choice)
> * build your mission statement based on interests for landslide disaster/emergency (politics/zoning, business/insurance, social/inequality, environmental/research)


References


- [How to setup a GitHub Organization, project and team](https://github.com/collab-uniba/socialcde4eclipse/wiki/How-to-setup-a-GitHub-organization,-project-and-team)
- [Creating GitHub Pages site](https://help.github.com/en/github/working-with-github-pages/creating-a-github-pages-site)
- [Creating and Hosting a Personal Site on GitHub](http://jmcglone.com/guides/github-pages/)
- [Simple navigation menus in Jekyll](https://learn.cloudcannon.com/jekyll/simple-navigation/)
- [Jekyll's directory structure](https://jekyllrb.com/docs/structure/)


## Day 3 / Week 4
The Physical Factors of Landslides by Hall & Walker, 2017  [(pptx)](https://d32ogoqmya1dw8.cloudfront.net/files/getsi/teaching_materials/surface_processes/unit_3_physical_factors.v6.pptx)

Material Strength and Landsliding Assessment by Hall & Walker, 2017 ([pptx](https://d32ogoqmya1dw8.cloudfront.net/files/getsi/teaching_materials/surface_processes/unit_3_strength_assessment.v12.pptx))

The Critical Rainfall Threshold Model (Eq. 28, [Iverson, 2000](https://doi.org/10.1029/2000WR900090))

```
     tan φ       C - ψt * γw * (tan φ)
Fs = -----  +  --------------------------
     tan θ     γr * H * (sin θ) * (cos θ)
```

where:

- Fs is the factor of safety
- φ is internal angle of friction (deg)
- θ is hillslope (deg)
- C is soil cohesion (Pa = kg/m/s^2)
- ψt is pressure head (m) = h * cosθ (Eq. 6, [Gabet et al., 2004](https://doi.org/10.1016/j.geomorph.2004.03.011))
- γw is unit weight of water (N/m^3); N=kg*m/s^2
- γr is unit weight of soil regolith (N/m^3)
- H is soil regolith thickness (m)

With knowledge of these variables, now we need to find the data to support them.

Skill Building Challenge: Highest US landslide density challenge

> Based on US landslide inventory, where is there the greatest density of landslide occurrence in square kilometers?
>

* find and download landslide point data
* in teams, come up with a method to solve the challenge

## Day 4 / Week 5
- Review challenge problem from last week
- Intro to Programming (to be continued on 2/24)
    - review example [Python script (.py)](/assets/scripts/example.py)
- Reading (Ch 2; [Geoprocessing with Python](https://livebook.manning.com/book/geoprocessing-with-python/chapter-2/1). Garrard, 2016).
