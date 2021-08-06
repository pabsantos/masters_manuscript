library(GWmodel)
library(rgdal)
library(tidyverse)
library(spdep)
library(tmap)

# Taz import and tidy ----

taz_gwr <- readOGR("input", "taz_quali")

taz_data_tidy <- function(taz_shape){
  
  taz_shape@data <- taz_shape@data %>% 
    mutate(prop = total_leng / road_l)
  
  taz_shape <- taz_shape[!is.na(taz_shape$freeflow_l),]
  
  taz_shape <- taz_shape[taz_shape$prop > 0.1,]
  
  taz_shape@data <- taz_shape@data %>% 
    select(-fid, -BAIRRO, -area, -total_leng, -freeflow_l, -speeding_l, -road_l, 
           -prop, -pop)
  
  return(taz_shape)
  
}

taz_gwr <- taz_data_tidy(taz_gwr)

# GWR function ----

gwr <- function(taz_shape){
  
  # Sort independent variables for best fit
  
  ind_var <- c("PD", "PAR", "DIS", "DSC", "DCSU", "AVI", "LDI", "BSD")
  
  sort_var <- function(taz){
    
    model_select <- model.selection.gwr(
      DeVar = "SP",
      InDeVars = ind_var,
      data = taz,
      bw = 30,
      approach = "AIC",
      kernel = "gaussian",
      adaptive = TRUE
    )
    
    return(as.formula(model_select[[1]][[36]][[1]]))
    
  }
  
  sorted_formula <- sort_var(taz_shape)
  
  # Extracting bw size for each kernel type
  kernel_type <- c("gaussian", "bisquare", "tricube", "boxcar", "exponential")
  
  bw_sizes <- vector(mode = "integer", length = 5)
  
  calc_bw_sizes <- function(kernel){
    
    bw.gwr(formula = sorted_formula, 
           data = taz_shape, 
           approach = "AIC", 
           kernel = kernel,
           adaptive = TRUE)
    
  }
  
  bw_sizes <- map_dbl(kernel_type, calc_bw_sizes)
  
  names(bw_sizes) <- kernel_type
  
  # Running a GWR for each kernel type
  gwr_calc <- function(bw, kernel){
    
    gwr.basic(formula = sorted_formula, 
              data = taz_shape, 
              bw = bw, 
              kernel = kernel, 
              adaptive = TRUE)
    
  }
  
  gwr_results <- vector(mode = "list", length = 5)
  
  gwr_results <- map2(bw_sizes, kernel_type, gwr_calc)

  return(gwr_results)
}

gwr_model_results <- gwr(taz_gwr) 

# Extracting diagnostic for each GWR model ---- 

extract_diagnostic <- function(gwr){
  
  df <- tibble(test = c("RSS.gw", "AIC", "AICc", "enp", "edf", "gw.R2", "gwR2.adj", "BIC",
                        "bandwidth"),
               gaussian = c(unlist(gwr[[1]][["GW.diagnostic"]]), 
                            gwr[["gaussian"]][["GW.arguments"]][["bw"]]), 
               bisquare = c(unlist(gwr[[2]][["GW.diagnostic"]]),
                            gwr[["bisquare"]][["GW.arguments"]][["bw"]]), 
               tricube =  c(unlist(gwr[[3]][["GW.diagnostic"]]),
                            gwr[["tricube"]][["GW.arguments"]][["bw"]]), 
               boxcar = c(unlist(gwr[[4]][["GW.diagnostic"]]),
                          gwr[["boxcar"]][["GW.arguments"]][["bw"]]),
               exponential = c(unlist(gwr[[5]][["GW.diagnostic"]]),
                               gwr[["exponential"]][["GW.arguments"]][["bw"]]))
}

diagnostic_table <- extract_diagnostic(gwr_model_results)

# Moran's I on residuals ----

calc_moran <- function(gwr_model_data){
  
  # Extracting neighbors
  nb <- poly2nb(gwr_model_data[[1]][["SDF"]], queen = TRUE)
  
  # Setting weights for each neighbor
  lw <- nb2listw(nb, style = "W", zero.policy = TRUE)
  
  # Moran's I with Monte Carlo Simulation for gwr
  gwr_mmc <- function(gwr_model_data){
    
    moran.mc(gwr_model_data[["SDF"]]$residual, lw, nsim = 999, alternative = "greater")
    
  }
  
  gwr_mmc_results <- map(gwr_model_data, gwr_mmc)
  
  global_mmc <- moran.mc(gwr_model_data[[1]][["lm"]]$residuals, lw, nsim = 999,
                         alternative = "greater")
  
  # Results table
  results <- tibble(
    model = c("gaussian", "bisquare", "tricube", "boxcar", "exponential", "global"),
    i = c(gwr_mmc_results[[1]][["statistic"]], gwr_mmc_results[[2]][["statistic"]],
                gwr_mmc_results[[3]][["statistic"]], gwr_mmc_results[[4]][["statistic"]],
                gwr_mmc_results[[5]][["statistic"]], global_mmc[["statistic"]]),
    p_value = c(gwr_mmc_results[[1]][["p.value"]], gwr_mmc_results[[2]][["p.value"]],
                gwr_mmc_results[[3]][["p.value"]], gwr_mmc_results[[4]][["p.value"]],
                gwr_mmc_results[[5]][["p.value"]], global_mmc[["p.value"]])
  )
  
  return(results)
  
}

morans_i <- calc_moran(gwr_model_results)

# Selecting best model ----
# manual process, check diagnostic (code to be implemented ...)

gwr_chosen_model <- gwr_model_results[[4]]

# GW summary on speeding (mean and SD maps) ----

summary_maps <- function(taz_shape){
  
  vars = c("SP", "PD", "PAR", "DIS", "DSC", "DCSU", "AVI", "LDI", "BSD")
  
  # Summary calc
  summary <- gwss(taz_shape,
                  vars = vars,
                  bw = gwr_chosen_model[["GW.arguments"]][["bw"]],
                  kernel = gwr_chosen_model[["GW.arguments"]][["kernel"]],
                  adaptive = TRUE,
                  quantile = TRUE)
 
  # Base map import
  taz <- st_read("input", "taz_quali")
  
  # Mean map
  sp_lm <- tm_shape(taz) + 
    tm_fill(col="grey") + 
    tm_borders(col="black", lwd=0.1) +
    tm_shape(summary[["SDF"]]) + 
    tm_fill(col="SP_LM", n = 6, style="quantile") + 
    tm_borders(col="black", lwd=0.2) + 
    tm_layout(frame=FALSE,) + 
    tm_legend(legend.position = c(0.8,0.08))
  
  # SD map
  sp_lsd <- tm_shape(taz) + 
    tm_fill(col="grey") + 
    tm_borders(col="black", lwd=0.1) +
    tm_shape(summary[["SDF"]]) + 
    tm_fill(col="SP_LSD", n = 6, style="quantile") + 
    tm_borders(col="black", lwd=0.2) + 
    tm_layout(frame=FALSE,) + 
    tm_legend(legend.position = c(0.8,0.08))
  
  results <- list(sp_lm, sp_lsd)
  
  names(results) <- c("sp_lm", "sp_lsd")
  
  return(results)
}

gwr_summary <- summary_maps(taz_gwr)

# Plot GWR results ----

plot_results <- function(gwr_model_data){
  
  # Import base map
  taz <- st_read("input", "taz_quali")
  
  # Variables
  vars <- c(colnames(gwr_model_data[["SDF"]]@data[2:9]), "Local_R2")
  
  make_maps <- function(var){
    
    maps <- tm_shape(taz) + 
      tm_fill(col="grey") + 
      tm_borders(col="black", lwd=0.1) +
      tm_shape(gwr_model_data[["SDF"]]) +
      tm_fill(col = var, n = 6, style = "quantile", palette = "-RdYlGn") +
      tm_borders(col="black", lwd = 0.2) +
      tm_layout(frame=FALSE, legend.width = 0.6) + 
      tm_legend(legend.position = c(0.8,0.08))
    
  }

  result_maps <- map(vars, make_maps)
  
  return(result_maps)
  
}

gwr_results_maps <- plot_results(gwr_chosen_model)

# Count positive and negative coefficients per TAZ and variable ----

make_results_table <- function(gwr_model_data){
  
  gwr_results <- gwr_model_data[["SDF"]]@data %>% 
    select(Intercept:LDI)
  
  gwr_results %>% 
    mutate(across(everything(), ~ case_when(
      . >= 0 ~ "pos",
      . < 0 ~ "neg",
      TRUE ~ NA_character_
    ))) %>% 
    pivot_longer(Intercept:LDI, names_to = "variables", values_to = "count") %>% 
    mutate(n = 1) %>% 
    group_by(variables, count) %>% 
    summarise(n = sum(n)) %>% 
    pivot_wider(names_from = count, values_from = n) %>% 
    replace(is.na(.), 0) %>% 
    mutate(prop_neg = neg / (neg+pos),
           prop_pos = pos / (neg+pos)) %>% 
    arrange(-prop_neg)
  
}

results_table <- make_results_table(gwr_chosen_model)
