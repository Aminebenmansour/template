# app/models/forum.rb
class Forum
    include Mongoid::Document
  
    store_in collection: 'Forums'
  
    field :title, type: String
    field :status, type: String
    field :visits, type: Integer
    field :data_size, type: String
    field :last_view, type: Time
    field :pub, type: Time
    field :full_url, type: String
  end
  