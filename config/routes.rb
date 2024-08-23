Rails.application.routes.draw do
  get 'forums/index'
  get 'home/index'
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Defines the root path route ("/")
  root 'forums#index'  # Notez que 'forums#index' doit correspondre à votre action dans le contrôleur Forums


  get "github_leaks", to: "github_leaks#index"
end