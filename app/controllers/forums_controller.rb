class ForumsController < ApplicationController
  def index
    @forums = Forum.all

    # Convertir les tailles de TBL en GBL et supprimer l'unité
    @forums.each do |forum|
      forum.update(data_size: convert_size_to_gb(forum.data_size))
      Rails.logger.info(":ssssssssssssss #{forum.title}")

    end
    @forums_by_data_size = @forums.sort_by { |forum| forum.data_size.to_f }.reverse
 
    # Trier les forums par nombre de visites en ordre décroissant
    @forums_by_visits = @forums.order(visits: :desc)
    

    # Trier les forums par date de publication en ordre décroissant
    @forums_by_date = @forums.order(pub: :desc)
    @map_data = prepare_map_data
    Rails.logger.info("Final Map Data: #{@map_data}") # Vérification après assignation
    
    
    


    # Calculer le nombre de forums pour chaque statut
    total_count = @forums.size
    published_count = @forums.where(status: 'PUBLISHED').count
    not_published_count = @forums.where(status: 'NOT PUBLISHED').count

    # Calculer les pourcentages 
    published_percentage = (published_count.to_f / total_count * 100).round(2)
    not_published_percentage = (not_published_count.to_f / total_count * 100).round(2)
    

    # Préparer les données pour le graphique en secteurs
    @status_data = [
      { name: 'Published', y: published_percentage },
      { name: 'Not Published', y: not_published_percentage }
    ]

    # Préparer les données pour le graphique linéaire
    @monthly_data = aggregate_data_by_month
  end

  private

  def convert_size_to_gb(size)
    return size unless size # Si la taille est nulle, retourner la valeur telle quelle
    
    if size.end_with?('TBL')
      size_value = size.gsub('TBL', '').to_f * 1024 # Convertir TBL en GBL (1 TBL = 1024 GBL)
    elsif size.end_with?('GBL')
      size_value = size.gsub('GBL', '').to_f # Retirer 'GBL' pour obtenir la valeur numérique
    else
      size_value = size.to_f # Si la taille a un autre format, retourner la valeur numérique brute
    end

    size_value
  end

  def aggregate_data_by_month
    # Initialiser un hash pour stocker les résultats
    monthly_counts = Hash.new(0)
    
    # Parcourir chaque forum et calculer les visites par mois
    @forums.each do |forum|
      next unless forum.pub.present?

      month_year = forum.pub.strftime('%b %Y')
      monthly_counts[month_year] += 1
    end

    # Trier les résultats par mois
    sorted_monthly_counts = monthly_counts.sort_by { |month, _| Date.parse(month) }
    
    # Extraire les mois et les valeurs
    months = sorted_monthly_counts.map(&:first)
    values = sorted_monthly_counts.map(&:last)
    
    { months: months, values: values }
  end
end
def prepare_map_data
  # Collecter les données des forums pour la carte
  grouped_forums = @forums.group_by(&:code3)
Rails.logger.info("Map Data: #{@grouped_forums}") # Vérification après assignation


  # Map the grouped data to the desired format
  map_data = grouped_forums.map do |code3, forums|
    {
      code3: code3,
      name: forums.first.country,
      value: forums.sum(&:visits)
    }

  end
  
  map_data
end