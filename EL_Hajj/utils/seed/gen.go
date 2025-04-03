package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"slices"
	"strconv"
	"strings"
	"time"
)

// password,last_login,email,is_email_verified,code,first_name,last_name,phone,dateOfBirth,province,gender,nombreInscription,role,winner,winning_date,personal_picture,city

type City struct {
    Id int
    Name string
    Province int
    Population int
}

func check(err error) {
    if (err != nil) {
        panic(err)
    }
}

var base int = 0
var mahramIds []int = []int{}
var registrationBase int = 0
// admin, doctor, drawing_manager, payment_manager, user, hajj
// accounts = 1 + 5 + 5 + 5 + 50 + 35
var roleCountArray []map[string]int = []map[string]int{
    { "admin": 1, },
    { "doctor": 5, },
    { "drawingManager": 5, },
    { "paymentManager": 5, },
    { "user": 50, },
    { "hajj": 40, },
}

var maleFirstNames []string = []string{ 
    "youness", "mohamed", "nadir", "abd-essamad", "abdou", "youcef", "ibrahim", "ayoub", "hamid", "yacoub",
}

var femaleFirstNames []string = []string { 
    "karima", "fatima", "aicha", "aya", "meriem", "manar", "yasmine", "khalida", "asmaa", "zainab",
}

var lastNames []string = []string {
    "merzouka", "rais", "chellal", "bourass", "fendi", "ameri", "boukennouche", "maredj", "krim", "hallouche", 
    "abahri", "benahmed", "hassi", "merzouk",
}

var arabicMaleFirstNames []string = []string{
    "يونس", "محمد", "ندير", "عبد الصمد", "عبدو", "يوسف", "إبراهيم", "أيوب", "حميد", "يعقوب",
}

var arabicFemaleFirstNames []string = []string{
    "كريمة", "فاطمة", "عائشة", "آية", "مريم", "منار", "ياسمين", "خاليدة", "أسماء", "زينب",
}

var arabicLastNames []string = []string{
    "مرزوقة", "رايس", "شلال", "بوراس", "فندي", "عمري", "بوقنوش", "مارج", "كريم", "حلوش",
    "أبحري", "بن أحمد", "حسي", "مرزوق",
}

func getFirstName(gender string) string {
    if (gender == "male") {
        return maleFirstNames[rand.Intn(len(maleFirstNames))];
    }
    return femaleFirstNames[rand.Intn(len(maleFirstNames))];
}

func getLastName() string {
    return lastNames[rand.Intn(len(lastNames))]
}

func getArabicFirstName(gender string) string {
    if (gender == "male") {
        return maleFirstNames[rand.Intn(len(arabicMaleFirstNames))];
    }
    return femaleFirstNames[rand.Intn(len(arabicFemaleFirstNames))];
}

func getArabicLastName() string {
    return lastNames[rand.Intn(len(arabicLastNames))]
}

func getGender() string {
    if (rand.Intn(2) == 1) {
        return "M"
    }
    return "F"
}

// admin, doctor, drawing_manager, payment_manager, user, hajj
func getEmail(city City, role string, index int) string {
    cityName := strings.Replace(strings.ToLower(city.Name), " ", "-", -1)
    cityName = strings.Replace(cityName, "'", "", -1)
    switch role {
    case "user":
        return fmt.Sprintf("%s-user%d@gmail.com", cityName, index)
    case "hajj":
        return fmt.Sprintf("%s-hajj%d@gmail.com", cityName, index)
    case "drawingManager":
        return fmt.Sprintf("%s-drawing-manager%d@gmail.com", cityName, index)
    case "paymentManager":
        return fmt.Sprintf("%s-payment-manager%d@gmail.com", cityName, index)
    case "doctor":
        return fmt.Sprintf("%s-doctor%d@gmail.com", cityName, index)
    case "admin":
        return fmt.Sprintf("%s-admin%d@gmail.com", cityName, index)
}
    panic("invalid role")
}

func genNumbers(count int) string {
    result := ""
    for i := 0; i < count; i++ {
        result += strconv.Itoa(rand.Intn(10))
    }
    return result
}

func getPhone() string {
    providers := []string{
        "5", "6", "7",
    }
    phone := fmt.Sprintf("+213-%s", providers[rand.Intn(len(providers))])
    phone += genNumbers(8)
    return phone
}

func getDateOfBirth() string {
    return time.Now().AddDate(-1 * (18 + rand.Intn(13)), -1 * (1 + rand.Intn(12)), -1 * (1 + rand.Intn(31))).Format("2006-01-02")
}

func getCity(cities []City) City {
    if (len(cities) > 0) {
        return cities[rand.Intn(len(cities))]
    }
    panic("invalid input to Intn")
}

func getRole(role string) string {
    /* ("user","user"),
("administrateur","administrateur"),
("responsable tirage","responsable tirage"),
("medecin","medecin"),
("Hedj","Hedj"),
("banquier","banquier"), */
    switch role {
    case "user":
        return "user"
    case "admin":
        return "administrateur"
    case "drawingManager":
        return "responsable tirage"
    case "doctor":
        return "medecin"
    case "hajj":
        return "Hedj"
    case "paymentManager":
        return "banquier"
}
    panic("invalid role")
}

func genLines(role string, cities []City, number int, passwords []string, passwordBase int) []string {
    result := []string{}
    // id,password,email,first_name,last_name,phone,dateOfBirth,province,gender,role,city
    for i := 0; i < number; i++ {
        id := passwordBase + i
        city := getCity(cities)
        genderAlias := getGender()
        gender := ""
        if (genderAlias == "F") {
            gender = "female"
        } else {
            gender = "male"
            if (role == "user") {
                mahramIds = append(mahramIds, id)
            }
        }
        // id,password,email,first_name,last_name,\"nombreInscription\",phone,\"dateOfBirth\",province,gender,role,winner,city
        result = append(result, fmt.Sprintf(
            "(%d,'%s','%s','%s','%s',%d,'%s','%s',%d,'%s','%s',%s,'%s')", 
            id,
            passwords[id],
            getEmail(city, role, i),
            getFirstName(gender),
            getLastName(),
            0,
            getPhone(),
            getDateOfBirth(),
            city.Province,
            genderAlias,
            getRole(role),
            "false",
            strings.Replace(city.Name, "'", "''", -1),
            ))
    }
    return result
}

func genHajjLines(
    role string,
    cities []City,
    number int,
    passwords []string,
    passwordBase int,
    firstNames []string,
    lastNames []string,
    genders []string,
) []string {
    result := []string{}
    // id,password,email,first_name,last_name,phone,dateOfBirth,province,gender,role,city
    for i := 0; i < number; i++ {
        city := getCity(cities)
        id := passwordBase + i
        gender := ""
        if (genders[i] == "male") {
            gender = "M"
        } else {
            gender = "F"
        }
        // id,password,email,first_name,last_name,\"nombreInscription\",phone,\"dateOfBirth\",province,gender,role,winner,city
        result = append(result, fmt.Sprintf(
            "(%d,'%s','%s','%s','%s',%d,'%s','%s',%d,'%s','%s',%s,'%s')", 
            id,
            passwords[id],
            getEmail(city, role, i),
            firstNames[i],
            lastNames[i],
            1,
            getPhone(),
            getDateOfBirth(),
            city.Province,
            gender,
            getRole(role),
            "false",
            strings.Replace(city.Name, "'", "''", -1),
            ))
    }
    return result
}

func getRoleCountCount(count map[string]int) int {
    for _, count := range count {
        return count
    }
    panic("empty map")
}

func getRoleCountRole(count map[string]int) string {
    for role := range count {
        return role
    }
    panic("empty map")
}

func getProvinces(cities []City) []int {
    provinces := []int{}
    for _, city := range cities {
        if (!slices.Contains(provinces, city.Province)) {
            provinces = append(provinces, city.Province)
        }
    }
    return provinces
}

func genUsers(
    cities []City,
    fistNames []string,
    lastNames []string,
    genders []string,
) {
    data, err := os.ReadFile("./passwords.txt")
    check(err)
    passwords := strings.Split(string(data), "\n")
    columns := "id,password,email,first_name,last_name,\"nombreInscription\",phone,\"dateOfBirth\",province,gender,role,winner,city"
    lines := []string{}
    index := base
    for _, roleCount := range roleCountArray {
        role := getRoleCountRole(roleCount)
        count := getRoleCountCount(roleCount)
        if (role == "hajj") {
            lines = append(lines, genHajjLines(role, cities, count, passwords, index, fistNames, lastNames, genders)...)
        } else {
            lines = append(lines, genLines(role, cities, count, passwords, index)...)
        }
        index += count
    }
    table_name := "authentication_user"
    query := fmt.Sprintf("INSERT INTO %s (%s) VALUES %s;", table_name, columns, strings.Join(lines, ",\n"))
    err = os.WriteFile("./queries/users.sql", []byte(query), 0644) 
    check(err)

}

func genAdminBaladiya(cities []City) []string {
    result := []string{}
    for _, city := range cities{
        result = append(result, fmt.Sprintf("(%d,%d)", city.Id, 0))
    }
    return result
}

func genUserBalaydiya(cities []City, adminBaladiyas []string) {
    index := base
    adminRoles := []string{
        "doctor",
        "drawingManager",
        "paymentManager",
    }
    result := []string{}
    for _, roleCount := range roleCountArray {
        role := getRoleCountRole(roleCount)
        count := getRoleCountCount(roleCount)
        if (slices.Contains(adminRoles, role)) {
            chosenCities := []int{}
            exit := false
            for {
                for i := 0; i < count; i++ {
                    cityId := 0
                    for {
                        cityId = cities[rand.Intn(len(cities))].Id
                        if (!slices.Contains(chosenCities, cityId)) {
                            break
                        }
                    }
                    chosenCities = append(chosenCities, cityId)
                    // baladiya_id, user_id
                    result = append(result, fmt.Sprintf(
                        "(%d,%d)",
                        cityId,
                        index + i,
                        ))
                    if (len(chosenCities) == len(cities)) {
                        exit = true
                        break
                    }
                }
                if (exit) {
                    break
                }
            }
        }
        index += count
    }
    result = append(result, adminBaladiyas...)
    err := os.WriteFile(
        "./queries/user_baladiya.sql", 
        []byte(fmt.Sprintf(
            "INSERT INTO registration_baladiya_id_utilisateur (baladiya_id,user_id) VALUES %s",
            strings.Join(result, ",\n"),
            )),
        0644,
        )
    check(err)
}



func getNIN() string {
    return genNumbers(10)
}

func getPassportId() string {
    return genNumbers(10)
}

func getExpirationDate() string {
    return time.Now().AddDate(2 + rand.Intn(6), rand.Intn(12), rand.Intn(30)).Format("2006-01-02")
}

func getAvailableMahramIds() []int {
    return mahramIds
}

func getAvailableUserIds() []int {
    ids := []int{}
    index := base
    for _, roleCount := range roleCountArray {
        role := getRoleCountRole(roleCount)
        count := getRoleCountCount(roleCount)
        if (role == "hajj") {
            for i := 0; i < count; i++ {
                ids = append(ids, index + i)
            }
            break
        }
        index += count
    }
    return ids
}

func getFirstNameIndex(gender string) int {
    if (gender == "male") {
        return rand.Intn(len(maleFirstNames))
    }
    return rand.Intn(len(femaleFirstNames))
}

func getLastNameIndex() int {
    return rand.Intn(len(lastNames))
}

func getArabicFirstNameAtIndex(gender string, index int) string {
    if (gender == "male") {
        return arabicMaleFirstNames[index]
    }
    return arabicFemaleFirstNames[index]
}

func getArabicLastNameAtIndex(index int) string {
    return arabicLastNames[index]
}

func getFirstNameAtIndex(gender string, index int) string {
    if (gender == "male") {
        return maleFirstNames[index]
    }
    return femaleFirstNames[index]
}

func getLastNameAtIndex(index int) string {
    return lastNames[index]
}

func getHajjNames() map[string][]string {
    count := 0
    for _, roleCount := range roleCountArray {
        if (getRoleCountRole(roleCount) == "hajj") {
            count = getRoleCountCount(roleCount)
            break
        }
    }
    genders := []string{}
    arabicFirstNames := []string{}
    arabicLastNames := []string{}
    firstNames := []string{}
    lastNames := []string{}
    for i := 0; i < count; i++ {
        gender := getGender()
        if (gender == "F") {
            gender = "female"
        } else {
            gender = "male"
        }
        genders = append(genders, gender)
        firstNameIndex := getFirstNameIndex(gender)
        lastNameIndex := getLastNameIndex()
        arabicFirstNames = append(arabicFirstNames, getArabicFirstNameAtIndex(gender, firstNameIndex))
        arabicLastNames = append(arabicLastNames, getArabicLastNameAtIndex(lastNameIndex))
        firstNames = append(firstNames, getFirstNameAtIndex(gender, firstNameIndex))
        lastNames = append(lastNames, getLastNameAtIndex(lastNameIndex))
    }
    return map[string][]string{
        "genders": genders,
        "firstNames": firstNames,
        "lastNames": lastNames,
        "arabicFirstNames": arabicFirstNames,
        "arabicLastNames": arabicLastNames,
    }
}

func genRegistrations(arabicFistNames []string, arabicLastNames []string, genders []string) {
    mahramIds := getAvailableMahramIds()
    userIds := getAvailableUserIds()
    result := []string{}
    for i, userId := range userIds {
        mahramId := ""
        if (genders[i] == "male") {
            mahramId = "null"
        } else {
            mahramId = strconv.Itoa(mahramIds[rand.Intn(len(mahramIds))])
        }
        result = append(result, fmt.Sprintf(
            "(%d,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,%s,'%s')",
            registrationBase + i,
            arabicFistNames[i],
            arabicLastNames[i],
            getFirstName("female"),
            getFirstName("male"),
            getNIN(),
            getExpirationDate(),
            getPassportId(),
            getExpirationDate(),
            "Algérienne",
            getPhone(),
            strconv.Itoa(userId),
            mahramId,
            "image/upload/v1715700815/qiyoqye42hplvtq3oywf.png",
            ))
    }
    columns := "(id,first_name_arabic,last_name_arabic,mother_name,father_name,\"NIN\",card_expiration_date,passport_id,passport_expiration_date,nationality,phone_number,user_id,maahram_id,personal_picture)"
    err := os.WriteFile("./queries/registrations.sql", []byte(fmt.Sprintf(
        "INSERT INTO registration_haaj %s VALUES %s",
        columns,
        strings.Join(result, ",\n"),
        )), 0644)
    check(err)
}

func main() {
    data, err := os.ReadFile("cities.json")
    check(err)

    var cities []City
    err = json.Unmarshal(data, &cities)
    check(err)
    available := getProvinces(cities)
    provinces := []int{}
    for i := 0; i < 3; i++ {
        provinces = append(provinces, available[rand.Intn(len(available))])
    }
    provinceCities := []City{}
    for _, city := range cities {
        if (slices.Contains(provinces, city.Province)) {
            provinceCities = append(provinceCities, city)
        }
    }
    names := getHajjNames()
    genUsers(provinceCities, names["firstNames"], names["lastNames"], names["genders"])
    genUserBalaydiya(provinceCities, genAdminBaladiya(cities))
    genRegistrations(names["arabicFirstNames"], names["arabicLastNames"], names["genders"])
}
